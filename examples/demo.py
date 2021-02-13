from eth_account.account import Account
from web3 import Web3, HTTPProvider
from web3._utils.transactions import wait_for_transaction_receipt
from web3.method import Method
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import Wei

from web3_flashbots import flashbot

# test miner account
faucet = Account.privateKeyToAccount("0x133be114715e5fe528a1b8adf36792160601a2d63ab59d1fd454275b31328791")
dummy_receiver = "0x1111111111111111111111111112144211111112"
user = Account.create("test")

if __name__ == '__main__':
    # instantiate Web3 as usual
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(faucet))
    # inject the new data
    flashbot(w3, flashbots_key_id="5", flashbots_secret="2", flashbots_url="http://localhost:8545")

    # faucet funds the user
    assert w3.eth.getBalance(user.address) == 0
    tx = w3.eth.sendTransaction({
        "from": faucet.address,
        "to": user.address,
        "value": w3.toWei("1.1", "ether"),
    })
    wait_for_transaction_receipt(w3, tx, 10, 1)
    assert w3.eth.getBalance(user.address) != 0

    nonce = w3.eth.getTransactionCount(user.address)
    bribe = w3.toWei('0.92', 'ether')

    signed_transaction = user.sign_transaction({
        "to": faucet.address,
        "value": bribe,
        "nonce": nonce + 1,
        "gasPrice": 0,
        "gas": 25000,
    })

    bundle = [
        #  some transaction
        {
            "signer": user,
            "transaction": {
                "to": dummy_receiver,
                "value": Wei(123),
                "nonce": nonce,
                "gasPrice": 0,
            }
        },
        # the bribe
        {
            "signed_transaction": signed_transaction.rawTransaction,
        }
    ]

    block_number = w3.eth.blockNumber
    block = w3.eth.blockNumber
    bal_before = w3.eth.getBalance(faucet.address, block)

    result = w3.flashbots.sendBundle(bundle, target_block_number = w3.eth.blockNumber + 3)
    result.wait()
    receipts = result.receipts()

    block_number = receipts[0].blockNumber

    # the miner has received the amount expected
    bal_before = w3.eth.getBalance(faucet.address, block_number - 1)
    bal_after = w3.eth.getBalance(faucet.address, block_number)
    profit = bal_after - bal_before - w3.toWei('2', 'ether') # sub block reward
    print("Balance before", bal_before)
    print("Balance after", bal_after)
    assert profit == bribe

    # the tx is successful
    assert w3.eth.getBalance(dummy_receiver) == 123
