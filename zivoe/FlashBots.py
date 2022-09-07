from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from flashbots import flashbot
from eth_account.account import Account

import os
import dotenv

dotenv.load_dotenv()

ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.getenv("KEEPER_0_PK"))

w3 = Web3(HTTPProvider("http://localhost:8545"))

# MAINNET
# flashbot(w3, ETH_ACCOUNT_SIGNATURE)

# GOERLI
flashbot(w3, ETH_ACCOUNT_SIGNATURE, "https://relay-goerli.flashbots.net")