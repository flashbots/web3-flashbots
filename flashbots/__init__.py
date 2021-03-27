from flashbots.flashbots import *

from web3 import Web3, HTTPProvider
from web3._utils.module import attach_modules

from .middleware import construct_flashbots_middleware

DEFAULT_FLASHBOTS_RELAY = "https://relay.flashbots.net"


def flashbot(
    w3: Web3,
    flashbots_url=DEFAULT_FLASHBOTS_RELAY,
):
    """
    Injects the flashbots module and middleware to w3.
    """
    flashbots_provider = HTTPProvider(flashbots_url)
    flash_middleware = construct_flashbots_middleware(flashbots_provider)
    w3.middleware_onion.add(flash_middleware)

    # attach modules to add the new namespace commands
    attach_modules(w3, {"flashbots": (Flashbots,)})
