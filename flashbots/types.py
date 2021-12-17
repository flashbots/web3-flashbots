from typing import TypedDict, List

from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3.types import TxParams


# unsigned transaction
FlashbotsBundleTx = TypedDict(
    "FlashbotsBundleTx",
    {
        "transaction": TxParams,
        "signer": LocalAccount,
    },
)

# signed transaction
FlashbotsBundleRawTx = TypedDict(
    "FlashbotsBundleRawTx",
    {
        "signed_transaction": HexBytes,
    },
)

# transaction dict taken from w3.eth.get_block('pending', full_transactions=True)
FlashbotsBundleDictTx = TypedDict(
    "FlashbotsBundleDictTx",
    {
        "accessList": list,
        "blockHash": HexBytes,
        "blockNumber": int,
        "chainId": str,
        "from": str,
        "gas": int,
        "gasPrice": int,
        "maxFeePerGas": int,
        "maxPriorityFeePerGas": int,
        "hash": HexBytes,
        "input": str,
        "nonce": int,
        "r": HexBytes,
        "s": HexBytes,
        "to": str,
        "transactionIndex": int,
        "type": str,
        "v": int,
        "value": int,
    },
    total=False,
)

FlashbotsOpts = TypedDict(
    "FlashbotsOpts",
    {"minTimestamp": int, "maxTimestamp": int, "revertingTxHashes": List[str]},
)
