from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from flashbots import flashbot
from eth_account.account import Account
from web3 import Web3, HTTPProvider, exceptions
from web3.types import TxParams

import os
import requests
import math

"""
In this example we setup a transaction for 0.1 eth with an appropriate gasprice.
From here we will use Flashbots to pass a bundle with the needed content.
"""

if not os.environ.get("SEND_TO") or not os.environ.get("ETH_PRIVATE_KEY"):
    print("env variables ETH_PRIVATE_KEY and SEND_TO required")
    exit(1)

# signifies your identify to the flashbots network
FLASHBOTS_SIGNATURE: LocalAccount = Account.create()
ETH_ACCOUNT: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_KEY"))
SEND_TO: str = os.environ.get("SEND_TO") # Eth address to send to

print("connecting to RPC")
w3 = Web3(HTTPProvider("http://localhost:8545"))
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(ETH_ACCOUNT))
flashbot(w3, FLASHBOTS_SIGNATURE)

print(f"account {ETH_ACCOUNT.address}: {w3.eth.get_balance(ETH_ACCOUNT.address)} wei")

# the bribe is contained in the gas price when not using a custom smart contract.
# it must be high enough to make all the transactions in the bundle have a 
# competative affective average gas price 
def get_gas_price():
    gas_api = 'https://ethgasstation.info/json/ethgasAPI.json'
    response = requests.get(gas_api).json()

    gas_multiplier = 10
    gas_price_gwei = math.floor(response["fastest"] / 10 * gas_multiplier)
    gas_price = w3.toWei(gas_price_gwei, 'gwei')
    return gas_price

# create a transaction
tx: TxParams = {
    "from": ETH_ACCOUNT.address,
    "to": w3.toChecksumAddress(SEND_TO),
    "value": w3.toWei("1.0", "gwei"),
    "gasPrice": get_gas_price(),
    "nonce": w3.eth.get_transaction_count(ETH_ACCOUNT.address),
}
tx["gas"] = math.floor(w3.eth.estimate_gas(tx) * 1.2)
signed_tx = ETH_ACCOUNT.sign_transaction(tx)
print(f'created transasction {signed_tx.hash.hex()}')
print(tx)

# create a flashbots bundle
bundle = [
    {"signed_transaction": signed_tx.rawTransaction},
    # you can include other transactions in the bundle 
    # in the order that you want them in the block
]

# flashbots bundles target a specific block, so we target
# any one of the next 3 blocks by emitting 3 bundles
block_number = w3.eth.block_number
for i in range(1, 3):
    w3.flashbots.send_bundle(bundle, target_block_number=block_number + i)
print(f'bundle broadcast at block {block_number}')

# wait for the transaction to get mined
tx_id = signed_tx.hash
while (True):
    try:      
        w3.eth.wait_for_transaction_receipt(
            tx_id, timeout=1, poll_latency=0.1
        )
        break

    except exceptions.TimeExhausted: 
        print(w3.eth.block_number)
        if w3.eth.block_number >= (block_number +3):
            print("ERROR: transaction was not mined")
            exit(1)
        
print(f'transaction confirmed at block {w3.eth.block_number}: {tx_id.hex()}')
