"""
Minimal viable example of flashbots usage with dynamic fee transactions.
Sends a bundle of two transactions which transfer some ETH into a random account.

"eth_sendBundle" is a generic method that can be used to send a bundle to any relay.
For instance, you can use the following relay URLs:
    titan: 'https://rpc.titanbuilder.xyz/'
    beaver: 'https://rpc.beaverbuild.org/'
    builder69: 'https://builder0x69.io/'
    rsync: 'https://rsync-builder.xyz/'
    flashbots: 'https://relay.flashbots.net'

You can simply replace the URL in the flashbot method to use a different relay like:
    flashbot(w3, signer, YOUR_CHOSEN_RELAY_URL)

Environment Variables:
- ETH_SENDER_KEY: Private key of account which will send the ETH.
- ETH_SIGNER_KEY: Private key of account which will sign the bundle. 
    - This account is only used for reputation on flashbots and should be empty.
- PROVIDER_URL: (Optional) HTTP JSON-RPC Ethereum provider URL. If not set, Flashbots Protect RPC will be used.
"""

import os
import secrets
from uuid import uuid4

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from web3 import HTTPProvider, Web3
from web3.exceptions import TransactionNotFound
from web3.types import TxParams

from flashbots import flashbot

# Define the network to use
NETWORK = "holesky"  # Options: "sepolia", "holesky", "mainnet"

# Define chain IDs and Flashbots Protect RPC URLs
NETWORK_CONFIG = {
    "sepolia": {
        "chain_id": 11155111,
        "provider_url": "https://rpc-sepolia.flashbots.net",
        "relay_url": "https://relay-sepolia.flashbots.net",
    },
    "holesky": {
        "chain_id": 17000,
        "provider_url": "https://rpc-holesky.flashbots.net",
        "relay_url": "https://relay-holesky.flashbots.net",
    },
    "mainnet": {
        "chain_id": 1,
        "provider_url": "https://rpc.flashbots.net",
        "relay_url": None,  # Mainnet uses default Flashbots relay
    },
}


def env(key: str) -> str:
    return os.environ.get(key)


def random_account() -> LocalAccount:
    key = "0x" + secrets.token_hex(32)
    return Account.from_key(key)


def main() -> None:
    # account to send the transfer and sign transactions
    sender: LocalAccount = Account.from_key(env("ETH_SENDER_KEY"))
    # account to receive the transfer
    receiverAddress: str = random_account().address
    # account to sign bundles & establish flashbots reputation
    # NOTE: this account should not store funds
    signer: LocalAccount = Account.from_key(env("ETH_SIGNER_KEY"))

    # Use user-provided RPC URL if available, otherwise use Flashbots Protect RPC
    user_provider_url = env("PROVIDER_URL")
    if user_provider_url:
        provider_url = user_provider_url
        print(f"Using user-provided RPC: {provider_url}")
    else:
        provider_url = NETWORK_CONFIG[NETWORK]["provider_url"]
        print(f"Using Flashbots Protect RPC: {provider_url}")

    w3 = Web3(HTTPProvider(provider_url))

    relay_url = NETWORK_CONFIG[NETWORK]["relay_url"]
    if relay_url:
        flashbot(w3, signer, relay_url)
    else:
        flashbot(w3, signer)

    print(f"Sender address: {sender.address}")
    print(f"Receiver address: {receiverAddress}")
    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiverAddress), 'ether')} ETH"
    )

    # bundle two EIP-1559 (type 2) transactions, pre-sign one of them
    # NOTE: chainId is necessary for all EIP-1559 txns
    # NOTE: nonce is required for signed txns

    nonce = w3.eth.get_transaction_count(sender.address)
    tx1: TxParams = {
        "to": receiverAddress,
        "value": Web3.toWei(0.001, "ether"),
        "gas": 21000,
        "maxFeePerGas": Web3.toWei(200, "gwei"),
        "maxPriorityFeePerGas": Web3.toWei(50, "gwei"),
        "nonce": nonce,
        "chainId": NETWORK_CONFIG[NETWORK]["chain_id"],
        "type": 2,
    }
    tx1_signed = sender.sign_transaction(tx1)

    tx2: TxParams = {
        "to": receiverAddress,
        "value": Web3.toWei(0.001, "ether"),
        "gas": 21000,
        "maxFeePerGas": Web3.toWei(200, "gwei"),
        "maxPriorityFeePerGas": Web3.toWei(50, "gwei"),
        "nonce": nonce + 1,
        "chainId": NETWORK_CONFIG[NETWORK]["chain_id"],
        "type": 2,
    }

    bundle = [
        {"signed_transaction": tx1_signed.rawTransaction},
        {"signer": sender, "transaction": tx2},
    ]

    # keep trying to send bundle until it gets mined
    while True:
        block = w3.eth.block_number

        # Simulation is only supported on mainnet
        if NETWORK == "mainnet":
            print(f"Simulating on block {block}")
            # Simulate bundle on current block.
            # If your RPC provider is not fast enough, you may get "block extrapolation negative"
            # error message triggered by "extrapolate_timestamp" function in "flashbots.py".
            try:
                w3.flashbots.simulate(bundle, block)
                print("Simulation successful.")
            except Exception as e:
                print("Simulation error", e)
                return

        # send bundle targeting next block
        print(f"Sending bundle targeting block {block+1}")
        replacement_uuid = str(uuid4())
        print(f"replacementUuid {replacement_uuid}")
        send_result = w3.flashbots.send_bundle(
            bundle,
            target_block_number=block + 1,
            opts={"replacementUuid": replacement_uuid},
        )
        print("bundleHash", w3.toHex(send_result.bundle_hash()))

        stats_v1 = w3.flashbots.get_bundle_stats(
            w3.toHex(send_result.bundle_hash()), block
        )
        print("bundleStats v1", stats_v1)

        stats_v2 = w3.flashbots.get_bundle_stats_v2(
            w3.toHex(send_result.bundle_hash()), block
        )
        print("bundleStats v2", stats_v2)

        send_result.wait()
        try:
            receipts = send_result.receipts()
            print(f"\nBundle was mined in block {receipts[0].blockNumber}\a")
            break
        except TransactionNotFound:
            print(f"Bundle not found in block {block+1}")
            # essentially a no-op but it shows that the function works
            cancel_res = w3.flashbots.cancel_bundles(replacement_uuid)
            print(f"canceled {cancel_res}")

    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiverAddress), 'ether')} ETH"
    )


if __name__ == "__main__":
    main()
