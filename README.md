# zivoe-mev-mitigation

This repository is responsible for fetching quotes from 1Inch APIs and automating calls to various contracts within the Zivoe protocol.

This repository is forked from flashbots, the existing README information is retained below this section.

All custom contracts implemented for the purpose of this repository are contained within the `/zivoe` directory.

Requires a `.env` file instantiated locally as follows:
```python
KEEPER_0_PK=
KEEPER_0_ADDY=
SWAPPER_0_ADDY=
INFURA_RPC_MAIN=
INFURA_RPC_GOERLI=
```
Where `KEEPER_0_PK` is the private key of the KEEPER given permission via ZivoeGlobals and `KEEPER_0_ADDY` is the corresponding address.
Where `SWAPPER_0_ADDY` is the contract address swapping assets (in live this will vary of course). 
Where `INFURA_RPC_MAIN` and `INFURA_RPC_GOERLI` are Infura-based endpoints for communicating with corresponding networks.

_Note: Do not add any spaces between values in the `.env`_

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

Install [poetry](https://python-poetry.org/)

Poetry will automatically fix your venv and all packages needed.

```sh
poetry install
```

Tips: PyCharm has a poetry plugin

## Simple Goerli Example

See [examples/simple.py](./examples/simple.py) for environment variable definitions.

```sh
poetry shell
ETH_SENDER_KEY=<sender_private_key> \
PROVIDER_URL=https://eth-goerli.alchemyapi.io/v2/<alchemy_key> \
ETH_SIGNER_KEY=<signer_private_key> \
python examples/simple.py
```

## Linting

It's advisable to run black with default rules for linting

```sh
sudo pip install black # Black should be installed with a global entrypoint
black .
```
