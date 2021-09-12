import os

from dotenv import load_dotenv

load_dotenv()
ALCHEMY_GOERLI_URI = os.environ["ALCHEMY_GOERLI_URI"]
FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE = os.environ["FLASHBOTS_GOERLI_ACCOUNT_SIGNATURE"]
