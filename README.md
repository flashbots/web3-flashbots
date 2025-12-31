# web3-flashbots

This library works by injecting flashbots as a new module in the Web3.py instance, which allows submitting "bundles" of transactions directly to miners. This is done by also creating a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends them to an RPC endpoint which you have specified, which corresponds to `mev-geth`.

To apply correct headers we use the `flashbot` method which injects the correct header on POST.

## Quickstart

```python
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from flashbots import flashbot
from eth_account.account import Account
import os

ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNER_KEY"))


w3 = Web3(HTTPProvider("http://localhost:8545"))
flashbot(w3, ETH_ACCOUNT_SIGNATURE)
```

Now the `w3.flashbots.sendBundle` method should be available to you. Look in [examples/simple.py](./examples/simple.py) for usage examples.

### Goerli

To use goerli, add the goerli relay RPC to the `flashbot` function arguments.

```python
flashbot(w3, ETH_ACCOUNT_SIGNATURE, "https://relay-goerli.flashbots.net")
```

## Development and testing

Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

```sh
uv sync --dev
```

## Simple Testnet Example

See [examples/simple.py](./examples/simple.py) for environment variable definitions.

```sh
ETH_SENDER_KEY=<sender_private_key> \
PROVIDER_URL=https://eth-holesky.g.alchemy.com/v2/<alchemy_key> \
ETH_SIGNER_KEY=<signer_private_key> \
uv run python examples/simple.py
```

## Linting

```sh
uv run ruff check .
uv run ruff format .
```
