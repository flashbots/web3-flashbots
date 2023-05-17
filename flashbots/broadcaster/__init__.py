from web3 import Web3
from web3._utils.module import attach_modules

from eth_account.signers.local import LocalAccount

from ..flashbots import Flashbots
from .broadcaster_provider import BroadcasterProvider
from .broadcaster_middleware import construct_broadcaster_middleware

from web3 import Web3


def broadcaster(w3: Web3, signature_account: LocalAccount, endpoint_uris: list) -> None:
    providers = BroadcasterProvider(signature_account, endpoint_uris)
    broadcaster_middleware = construct_broadcaster_middleware(providers)
    w3.middleware_onion.add(broadcaster_middleware)

    # attach modules to add the new namespace commands
    attach_modules(w3, {"flashbots": (Flashbots,)})
