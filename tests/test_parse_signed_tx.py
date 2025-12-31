# tests/test_parse_signed_tx.py

from eth_account import Account
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3

from flashbots.flashbots import _parse_signed_tx

# On utilise une clé privée de test déterministe (aucun danger ici)
PRIVATE_KEY = "0x" + "11" * 32
account: LocalAccount = Account.from_key(PRIVATE_KEY)


def test_parse_legacy_signed_tx():
    w3 = Web3()

    # Legacy tx: no "type" field, uses gasPrice
    tx = {
        "to": w3.to_checksum_address("0x000000000000000000000000000000000000dEaD"),
        "value": w3.to_wei(1, "ether"),
        "gas": 21000,
        "nonce": 0,
        "chainId": 1,
        "gasPrice": w3.to_wei(50, "gwei"),
        "data": b"",
    }

    signed = account.sign_transaction(tx)
    decoded = _parse_signed_tx(HexBytes(signed.raw_transaction))

    # Numeric fields have been converted to int
    assert decoded["chainId"] == tx["chainId"]
    assert decoded["nonce"] == tx["nonce"]
    assert decoded["gas"] == tx["gas"]
    assert decoded["value"] == tx["value"]
    assert decoded["gasPrice"] == tx["gasPrice"]

    # Address matches (case-insensitive)
    assert HexBytes(decoded["to"]) == HexBytes(tx["to"])

    # EIP-1559 fields should not be present
    assert "maxFeePerGas" not in decoded
    assert "maxPriorityFeePerGas" not in decoded


def test_parse_access_list_signed_tx():
    w3 = Web3()

    # EIP-2930 Access List tx: type=1, uses gasPrice and accessList
    tx = {
        "to": w3.to_checksum_address("0x000000000000000000000000000000000000dEaD"),
        "value": w3.to_wei(1, "ether"),
        "gas": 30000,
        "nonce": 1,
        "chainId": 1,
        "gasPrice": w3.to_wei(20, "gwei"),
        "type": 1,
        "data": b"",
        "accessList": [],
    }

    signed = account.sign_transaction(tx)
    decoded = _parse_signed_tx(HexBytes(signed.raw_transaction))

    # Numeric fields
    assert decoded["chainId"] == tx["chainId"]
    assert decoded["nonce"] == tx["nonce"]
    assert decoded["gas"] == tx["gas"]
    assert decoded["value"] == tx["value"]
    assert decoded["gasPrice"] == tx["gasPrice"]

    # Access list round-trips correctly
    assert decoded["accessList"] == tx["accessList"]

    # EIP-1559 fields should not be present here
    assert "maxFeePerGas" not in decoded
    assert "maxPriorityFeePerGas" not in decoded
    

def test_parse_eip1559_signed_tx():
    tx = {
        "to": Web3.to_checksum_address("0x000000000000000000000000000000000000dead"),
        "value": Web3.to_wei(1, "ether"),
        "gas": 21000,
        "nonce": 0,
        "chainId": 1,
        "maxFeePerGas": Web3.to_wei(100, "gwei"),
        "maxPriorityFeePerGas": Web3.to_wei(2, "gwei"),
        "type": 2,  # EIP-1559
        "data": b"",
        "accessList": [],
    }

    signed = account.sign_transaction(tx)
    decoded = _parse_signed_tx(HexBytes(signed.raw_transaction))

    assert HexBytes(decoded["to"]) == HexBytes(tx["to"])
    assert int(decoded["value"]) == tx["value"]
    assert int(decoded["nonce"]) == tx["nonce"]
    assert int(decoded["gas"]) == tx["gas"]
    assert int(decoded["maxFeePerGas"]) == tx["maxFeePerGas"]
    assert int(decoded["maxPriorityFeePerGas"]) == tx["maxPriorityFeePerGas"]
    assert int(decoded["chainId"]) == tx["chainId"]
