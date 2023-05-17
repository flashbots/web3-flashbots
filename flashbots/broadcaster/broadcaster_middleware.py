from web3 import Web3

from typing import Callable
from web3 import Web3
from web3.middleware import Middleware
from web3.types import RPCEndpoint, RPCResponse
from typing import Any

BUILDER_METHODS = [
    "eth_sendBundle",
]


def construct_broadcaster_middleware(broadcaster_provider) -> Middleware:
    def flashbots_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            if method not in BUILDER_METHODS:
                return make_request(method, params)
            else:
                resp = None
                resp = broadcaster_provider.make_request(method, params)
                return {"result": [resp]}

        return middleware

    return flashbots_middleware
