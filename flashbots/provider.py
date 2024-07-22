import logging
import os
from typing import Any, Dict, Optional, Union

from eth_account import Account, messages
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from web3 import HTTPProvider, Web3
from web3._utils.request import make_post_request
from web3.types import RPCEndpoint, RPCResponse


def get_default_endpoint() -> URI:
    return URI(
        os.environ.get("FLASHBOTS_HTTP_PROVIDER_URI", "https://relay.flashbots.net")
    )


class FlashbotProvider(HTTPProvider):
    """
    A custom HTTP provider for submitting transactions to Flashbots.

    This provider extends the standard Web3 HTTPProvider specifically to add the
    required 'X-Flashbots-Signature' header for Flashbots request authentication.

    Key features:
    - Automatically signs and includes the Flashbots-specific header with each request.
    - Uses a designated account for signing Flashbots messages.
    - Maintains compatibility with standard Web3 provider interface.

    :param signature_account: LocalAccount used for signing Flashbots messages.
    :param endpoint_uri: URI of the Flashbots endpoint. Defaults to the standard Flashbots relay.
    :param request_kwargs: Additional keyword arguments for requests.
    :param session: Session object to use for requests.

    Usage:
        flashbots_provider = FlashbotProvider(signature_account)
        w3 = Web3(flashbots_provider)
    """

    logger = logging.getLogger("web3.providers.FlashbotProvider")

    def __init__(
        self,
        signature_account: LocalAccount,
        endpoint_uri: Optional[Union[URI, str]] = None,
        request_kwargs: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
    ):
        """
        Initialize the FlashbotProvider.

        :param signature_account: The account used for signing messages.
        :param endpoint_uri: The URI of the Flashbots endpoint.
        :param request_kwargs: Additional keyword arguments for requests.
        :param session: The session object to use for requests.
        """
        _endpoint_uri = endpoint_uri or get_default_endpoint()
        super().__init__(_endpoint_uri, request_kwargs, session)
        self.signature_account = signature_account

    def _get_flashbots_headers(self, request_data: bytes) -> Dict[str, str]:
        message = messages.encode_defunct(
            text=Web3.keccak(text=request_data.decode("utf-8")).hex()
        )
        signed_message = Account.sign_message(
            message, private_key=self.signature_account._private_key
        )
        return {
            "X-Flashbots-Signature": f"{self.signature_account.address}:{signed_message.signature.hex()}"
        }

    def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        """
        Make a request to the Flashbots endpoint.

        :param method: The RPC method to call.
        :param params: The parameters for the RPC method.
        :return: The RPC response.
        """
        self.logger.debug(
            f"Making request HTTP. URI: {self.endpoint_uri}, Method: {method}"
        )
        request_data = self.encode_rpc_request(method, params)

        raw_response = make_post_request(
            self.endpoint_uri,
            request_data,
            headers=self.get_request_headers()
            | self._get_flashbots_headers(request_data),
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug(
            f"Getting response HTTP. URI: {self.endpoint_uri}, Method: {method}, Response: {response}"
        )
        return response
