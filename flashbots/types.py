from eth_account.signers.local import LocalAccount
from eth_typing import HexStr
from hexbytes import HexBytes
from typing import TypedDict, List, Union
from web3.types import TxParams, _Hash32


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

# type alias
TxReceipt = Union[_Hash32, HexBytes, HexStr]

# response from bundle or private tx submission
SignedTxAndHash = TypedDict(
    "SignedTxAndHash",
    {
        "signed_transaction": str,
        "hash": HexBytes,
    },
)
