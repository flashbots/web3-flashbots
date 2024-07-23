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

import logging
import os
import secrets
from uuid import uuid4

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from web3 import HTTPProvider, Web3
from web3.exceptions import TransactionNotFound
from web3.types import Nonce, TxParams

from flashbots import FlashbotsWeb3, flashbot
from flashbots.constants import FLASHBOTS_NETWORKS
from flashbots.types import NetworkType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the network to use
NETWORK: NetworkType = "holesky"  # Options: "sepolia", "holesky", "mainnet"


def env(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' is not set")
    return value


def random_account() -> LocalAccount:
    key = "0x" + secrets.token_hex(32)
    return Account.from_key(key)


def get_account_from_env(key: str) -> LocalAccount:
    return Account.from_key(env(key))


def setup_web3(network: str) -> FlashbotsWeb3:
    provider_url = os.environ.get(
        "PROVIDER_URL", FLASHBOTS_NETWORKS[network]["provider_url"]
    )
    logger.info(f"Using RPC: {provider_url}")
    relay_url = FLASHBOTS_NETWORKS[network]["relay_url"]
    w3 = flashbot(
        Web3(HTTPProvider(provider_url)),
        get_account_from_env("ETH_SIGNER_KEY"),
        relay_url,
    )
    return w3


def log_account_balances(w3: Web3, sender: str, receiver: str) -> None:
    logger.info(
        f"Sender account balance: {Web3.from_wei(w3.eth.get_balance(Web3.to_checksum_address(sender)), 'ether')} ETH"
    )
    logger.info(
        f"Receiver account balance: {Web3.from_wei(w3.eth.get_balance(Web3.to_checksum_address(receiver)), 'ether')} ETH"
    )


def create_transaction(w3: Web3, sender: str, receiver: str, nonce: int) -> TxParams:
    return {
        "to": receiver,
        "value": Web3.to_wei(0.001, "ether"),
        "gas": 21000,
        "maxFeePerGas": Web3.to_wei(200, "gwei"),
        "maxPriorityFeePerGas": Web3.to_wei(50, "gwei"),
        "nonce": Nonce(nonce),
        "chainId": FLASHBOTS_NETWORKS[NETWORK]["chain_id"],
        "type": 2,
    }


def main() -> None:
    sender = get_account_from_env("ETH_SENDER_KEY")
    receiver = random_account().address
    w3 = setup_web3(NETWORK)

    logger.info(f"Sender address: {sender.address}")
    logger.info(f"Receiver address: {receiver}")
    log_account_balances(w3, sender.address, receiver)

    nonce = w3.eth.get_transaction_count(sender.address)
    tx1 = create_transaction(w3, sender.address, receiver, nonce)
    tx2 = create_transaction(w3, sender.address, receiver, nonce + 1)

    tx1_signed = sender.sign_transaction(tx1)
    bundle = [
        {"signed_transaction": tx1_signed.rawTransaction},
        {"transaction": tx2, "signer": sender},
    ]

    # keep trying to send bundle until it gets mined
    while True:
        block = w3.eth.block_number

        # Simulation is only supported on mainnet
        if NETWORK == "mainnet":
            # Simulate bundle on current block.
            # If your RPC provider is not fast enough, you may get "block extrapolation negative"
            # error message triggered by "extrapolate_timestamp" function in "flashbots.py".
            try:
                w3.flashbots.simulate(bundle, block)
            except Exception as e:
                logger.error("Simulation error", e)
                return

        # send bundle targeting next block
        replacement_uuid = str(uuid4())
        logger.info(f"replacementUuid {replacement_uuid}")
        send_result = w3.flashbots.send_bundle(
            bundle,
            target_block_number=block + 1,
            opts={"replacementUuid": replacement_uuid},
        )
        logger.info(f"bundleHash {w3.to_hex(send_result.bundle_hash())}")

        stats_v1 = w3.flashbots.get_bundle_stats(
            w3.to_hex(send_result.bundle_hash()), block
        )
        logger.info(f"bundleStats v1 {stats_v1}")

        stats_v2 = w3.flashbots.get_bundle_stats_v2(
            w3.to_hex(send_result.bundle_hash()), block
        )
        logger.info(f"bundleStats v2 {stats_v2}")

        send_result.wait()
        try:
            receipts = send_result.receipts()
            logger.info(f"Bundle was mined in block {receipts[0].blockNumber}")
            break
        except TransactionNotFound:
            logger.info(f"Bundle not found in block {block + 1}")
            cancel_res = w3.flashbots.cancel_bundles(replacement_uuid)
            logger.info(f"Canceled {cancel_res}")

    log_account_balances(w3, sender.address, receiver)


if __name__ == "__main__":
    main()
