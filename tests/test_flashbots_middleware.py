# tests/test_flashbots_middleware.py

from flashbots.middleware import (FLASHBOTS_METHODS,
                                  construct_flashbots_middleware)
from web3 import Web3
from web3.providers.base import BaseProvider


class DummyProvider(BaseProvider):
    def make_request(self, method, params):
        # Retourne un JSON-RPC valide
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"fallback": method}
        }


class MockFlashbotProvider(DummyProvider):
    def make_request(self, method, params):
        # Retourne un JSON-RPC valide
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"flashbots": method}
        }


def test_flashbots_middleware_routing():
    w3 = Web3(DummyProvider())

    flashbots_provider = MockFlashbotProvider()
    middleware = construct_flashbots_middleware(flashbots_provider)

    # Inject middleware v7-style
    w3.middleware_onion.add(middleware)

    # Toutes les méthodes Flashbots doivent passer par MockFlashbotProvider
    for method in FLASHBOTS_METHODS:
        response = w3.manager.request_blocking(method, [])
        assert response == {"flashbots": method}, f"Method {method} not routed"

    # Les méthodes normales restent sous DummyProvider
    result = w3.manager.request_blocking("eth_blockNumber", [])
    assert result == {"fallback": "eth_blockNumber"}
