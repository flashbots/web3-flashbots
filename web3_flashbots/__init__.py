from .middleware import construct_flashbots_middleware
from .types import *
from .flashbots import Flashbots
from web3 import Web3, HTTPProvider
from web3._utils.module import attach_modules

DEFAULT_FLASHBOTS_RELAY = 'https://relay.flashbots.net'

def flashbot(w3: Web3, flashbots_key_id: str, flashbots_secret, flashbots_url = DEFAULT_FLASHBOTS_RELAY):
    """ 
        Injects the flashbots module and middleware to w3.
    """
    headers = {
        "Authorization": flashbots_key_id + ":" + flashbots_secret , # auth
        "Content-type": "application/json", # need to set the header again
    }
    flashbots_provider = HTTPProvider(flashbots_url, request_kwargs = { 'headers': headers })
    middleware = construct_flashbots_middleware(flashbots_provider)
    w3.middleware_onion.add(middleware)

    # attach modules to add the new namespace commands
    attach_modules(w3, { "flashbots" : (Flashbots,) })
