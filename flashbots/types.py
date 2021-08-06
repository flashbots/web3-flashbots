from eth_account.account import Account
from web3.types import TxParams
from typing import TypedDict, List
from hexbytes import HexBytes

FlashbotsBundleTx = TypedDict(
    "FlashbotsBundleTx",
    {
        "transaction": TxParams,
        "signer": Account,
    },
)

FlashbotsBundleRawTx = TypedDict(
    "FlashbotsBundleRawTx",
    {
        "signed_transaction": str,
    },
)

FlashbotsBundleDictTx = TypedDict(
    "FlashbotsBundleDictTx",
    {
        "blockHash": HexBytes,
        "blockNumber": int,
        "from": str,
        "gas": int,
        "gasPrice": int,
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
)

FlashbotsOpts = TypedDict(
    "FlashbotsOpts",
    {"minTimestamp": int, "maxTimestamp": int, "revertingTxHashes": List[str]},
)


# Type missing from eth_account, not really a part of flashbots web3 per sé
SignTx = TypedDict(
    "SignTx",
    {
        "nonce": int,
        "chainId": int,
        "to": str,
        "data": str,
        "value": int,
        "gas": int,
        "gasPrice": int,
    },
    total=False,
)
