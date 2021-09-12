import os


from dotenv import load_dotenv
from eth_account.signers.local import LocalAccount
from eth_account.account import Account
from web3 import Web3, WebsocketProvider
from flashbots import flashbot

load_dotenv()
ALCHEMY_GOERLI_URI = os.environ["ALCHEMY_GOERLI_URI"]
FLASHBOTS_ACCOUNT_SIGNATURE = os.environ["FLASHBOTS_ACCOUNT_SIGNATURE"]

w3 = Web3(WebsocketProvider(ALCHEMY_GOERLI_URI))
FLASHBOTS_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(FLASHBOTS_ACCOUNT_SIGNATURE)

flashbot(w3, FLASHBOTS_ACCOUNT_SIGNATURE)
print("gucci")