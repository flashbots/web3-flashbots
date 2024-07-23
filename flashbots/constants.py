from typing import Dict, Tuple

from eth_typing import URI

from .types import Network, NetworkConfig

FLASHBOTS_NETWORKS: Dict[Network, NetworkConfig] = {
    "sepolia": {
        "chain_id": 11155111,
        "provider_url": URI("https://rpc-sepolia.flashbots.net"),
        "relay_url": URI("https://relay-sepolia.flashbots.net"),
    },
    "holesky": {
        "chain_id": 17000,
        "provider_url": URI("https://rpc-holesky.flashbots.net"),
        "relay_url": URI("https://relay-holesky.flashbots.net"),
    },
    "mainnet": {
        "chain_id": 1,
        "provider_url": URI("https://rpc.flashbots.net"),
        "relay_url": URI("https://relay.flashbots.net"),
    },
}


def get_networks() -> Tuple[Network, ...]:
    return tuple(FLASHBOTS_NETWORKS.keys())
