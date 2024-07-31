"""
Minimal viable example of flashbots usage with dynamic fee transactions.
Sends a bundle of two transactions which transfer some ETH into a random account.

Environment Variables:
- ETH_SENDER_KEY: Private key of account which will send the ETH.
- ETH_SIGNER_KEY: Private key of account which will sign the bundle.
    - This account is only used for reputation on flashbots and should be empty.
- PROVIDER_URL: (Optional) HTTP JSON-RPC Ethereum provider URL. If not set, Flashbots Protect RPC will be used.
- LOG_LEVEL: (Optional) Set the logging level. Default is 'INFO'. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL.

Usage:
python examples/simple.py <network> [--log-level LEVEL]

Arguments:
- network: The network to use (e.g., mainnet, goerli)
- --log-level: (Optional) Set the logging level. Default is 'INFO'.

Example:
LOG_LEVEL=DEBUG python examples/simple.py mainnet --log-level DEBUG
"""

import argparse
import logging
import os
import secrets
from enum import Enum
from uuid import uuid4

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from web3 import HTTPProvider, Web3
from web3.exceptions import TransactionNotFound
from web3.types import TxParams

from flashbots import FlashbotsWeb3, flashbot
from flashbots.constants import FLASHBOTS_NETWORKS
from flashbots.types import Network

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class EnumAction(argparse.Action):
    def __init__(self, **kwargs):
        enum_type = kwargs.pop("type", None)
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum_type, Enum):
            raise TypeError("type must be an Enum when using EnumAction")
        kwargs.setdefault("choices", tuple(e.value for e in enum_type))
        super(EnumAction, self).__init__(**kwargs)
        self._enum = enum_type

    def __call__(self, parser, namespace, values, option_string=None):
        value = self._enum(values)
        setattr(namespace, self.dest, value)


def parse_arguments() -> Network:
    parser = argparse.ArgumentParser(description="Flashbots simple example")
    parser.add_argument(
        "network",
        type=Network,
        action=EnumAction,
        help=f"The network to use ({', '.join(e.value for e in Network)})",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    args = parser.parse_args()
    return args.network


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


def setup_web3(network: Network) -> FlashbotsWeb3:
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


def create_transaction(
    w3: Web3, sender: str, receiver: str, nonce: int, network: Network
) -> TxParams:
    # Get the latest gas price information
    latest = w3.eth.get_block("latest")
    base_fee = latest["baseFeePerGas"]

    # Set max priority fee (tip) to 2 Gwei
    max_priority_fee = Web3.to_wei(2, "gwei")

    # Set max fee to be base fee + priority fee
    max_fee = base_fee + max_priority_fee

    return {
        "from": sender,
        "to": receiver,
        "gas": 21000,
        "value": Web3.to_wei(0.001, "ether"),
        "nonce": nonce,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "chainId": FLASHBOTS_NETWORKS[network]["chain_id"],
    }


def main() -> None:
    network = parse_arguments()
    sender = get_account_from_env("ETH_SENDER_KEY")
    receiver = Account.create().address
    w3 = setup_web3(network)

    logger.info(f"Sender address: {sender.address}")
    logger.info(f"Receiver address: {receiver}")
    log_account_balances(w3, sender.address, receiver)

    nonce = w3.eth.get_transaction_count(sender.address)
    tx1 = create_transaction(w3, sender.address, receiver, nonce, network)
    tx2 = create_transaction(w3, sender.address, receiver, nonce + 1, network)

    tx1_signed = w3.eth.account.sign_transaction(tx1, private_key=sender.key)
    bundle = [
        {"signed_transaction": tx1_signed.rawTransaction},
        {"transaction": tx2, "signer": sender},
    ]

    # keep trying to send bundle until it gets mined
    while True:
        block = w3.eth.block_number

        # Simulation is only supported on mainnet
        if network == "mainnet":
            # Simulate bundle on current block.
            # If your RPC provider is not fast enough, you may get "block extrapolation negative"
            # error message triggered by "extrapolate_timestamp" function in "flashbots.py".
            try:
                w3.flashbots.simulate(bundle, block)
            except Exception as e:
                logger.error(f"Simulation error: {e}")
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
