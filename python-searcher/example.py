
from eth_account.signers.local import LocalAccount
from eth_account.account import Account
from web3 import Web3, WebsocketProvider
from flashbots import flashbot
from settings import ALCHEMY_GOERLI_URI, FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE

w3 = Web3(WebsocketProvider(ALCHEMY_GOERLI_URI))
FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE)

fb = flashbot(w3, FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE)
print("gucci")
