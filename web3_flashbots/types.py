from eth_account.account import Account
from web3.types import TxParams
from typing import TypedDict

FlashbotsBundleTx = TypedDict("FlashbotsBundleTx", {
    "transaction": TxParams,
    "signer": Account,
})

FlashbotsBundleRawTx = TypedDict("FlashbotsBundleRawTx", {
    "signed_transaction": str,
})

FlashbotsOpts = TypedDict("FlashbotsOpts", {
    "minTimestamp": int,
    "maxTimestamp": int,
})
