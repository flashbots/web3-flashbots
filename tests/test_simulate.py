# tests/test_simulate.py

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3._utils.module import attach_modules

from flashbots.flashbots import Flashbots

PRIVATE_KEY = "0x" + "22" * 32
account: LocalAccount = Account.from_key(PRIVATE_KEY)


def _flashbots_module() -> Flashbots:
    w3 = Web3()
    attach_modules(w3, {"flashbots": (Flashbots,)})
    return w3.flashbots


def test_simulate_accepts_int_block_tag():
    flashbots = _flashbots_module()

    tx = {
        "to": Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD"),
        "value": Web3.to_wei(1, "ether"),
        "gas": 21000,
        "nonce": 0,
        "chainId": 1,
        "gasPrice": Web3.to_wei(10, "gwei"),
        "data": b"",
    }
    signed = account.sign_transaction(tx)
    bundle = [{"signed_transaction": signed.raw_transaction}]

    captured = {}

    def fake_call_bundle(signed_bundled_transactions, evm_block_number, evm_block_state_number, evm_timestamp):
        captured["signed"] = signed_bundled_transactions
        captured["block_number"] = evm_block_number
        captured["state_block_number"] = evm_block_state_number
        captured["timestamp"] = evm_timestamp
        return {
            "bundleHash": "0x" + "00" * 32,
            "coinbaseDiff": "0x0",
            "results": [{"gasUsed": 21000}],
        }

    flashbots.call_bundle = fake_call_bundle

    result = flashbots.simulate(
        bundle,
        block_tag=10,
        state_block_tag=None,
        block_timestamp=123,
    )

    assert captured["block_number"] == "0xa"
    assert captured["state_block_number"] == "0x9"
    assert captured["timestamp"] == 123
    assert result["totalGasUsed"] == 21000
