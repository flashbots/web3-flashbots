import logging
import os
import json
from typing import Any, Union, Optional

from eth_account import Account, messages
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from web3 import HTTPProvider
from web3._utils.request import make_post_request
from web3.types import RPCEndpoint, RPCResponse
from web3 import Web3

from itertools import repeat
from concurrent import futures


def _make_post_request_wrapper(args):
    return make_post_request(args[0], args[1], headers=args[2])


class BroadcasterProvider(HTTPProvider):
    logger = logging.getLogger("web3.providers.FlashbotProvider")

    def __init__(
        self,
        signature_account: LocalAccount,
        endpoint_uris: Optional[Union[URI, str]] = None,
        request_kwargs: Optional[Any] = None,
        session: Optional[Any] = None,
    ):
        _endpoint_uri = endpoint_uris[0]
        self.endpoint_uris = endpoint_uris
        super().__init__(_endpoint_uri, request_kwargs, session)
        self.signature_account = signature_account
        self.executor = futures.ThreadPoolExecutor(max_workers=len(endpoint_uris))

    def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        self.logger.debug(
            "BroadcasterProvider Making request HTTP. URI: %s, Method: %s",
            self.endpoint_uris,
            method,
        )
        request_data = self.encode_rpc_request(method, params)

        message = messages.encode_defunct(
            text=Web3.keccak(text=request_data.decode("utf-8")).hex()
        )
        signed_message = Account.sign_message(
            message, private_key=self.signature_account.privateKey.hex()
        )

        headers = self.get_request_headers() | {
            "X-Flashbots-Signature": f"{self.signature_account.address}:{signed_message.signature.hex()}"
        }

        responses = self.executor.map(
            _make_post_request_wrapper,
            [
                (endpoint_uri, request_data, headers)
                for endpoint_uri in self.endpoint_uris
            ],
        )
        responses = [json.loads(r) for r in responses]

        response = [
            x["result"]["bundleHash"]
            for x in responses
            if "result" in x and x["result"] and ("bundleHash" in x["result"])
        ]

        return response
