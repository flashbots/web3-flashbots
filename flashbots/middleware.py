from typing import Any, Type

from web3 import Web3
from web3.types import RPCEndpoint, RPCResponse

from .provider import FlashbotProvider

FLASHBOTS_METHODS = [
    "eth_sendBundle",
    "eth_callBundle",
    "eth_cancelBundle",
    "eth_sendPrivateTransaction",
    "eth_cancelPrivateTransaction",
    "flashbots_getBundleStats",
    "flashbots_getUserStats",
    "flashbots_getBundleStatsV2",
    "flashbots_getUserStatsV2",
]


def construct_flashbots_middleware(
    flashbots_provider: FlashbotProvider,
) -> Type:
    """
    Returns a Web3.py v7-compatible middleware class.
    Inject it using:
        w3.middleware_onion.add(construct_flashbots_middleware(provider))
    """
    class FlashbotsMiddleware:
        def __init__(self, w3: Web3):
            self.w3 = w3
            self.flashbots_provider = flashbots_provider

        def wrap_make_request(self, make_request):
            # This method is called by combine_middleware
            def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
                if method in FLASHBOTS_METHODS:
                    return self.flashbots_provider.make_request(method, params)
                return make_request(method, params)
            return middleware

    return FlashbotsMiddleware
