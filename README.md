# WORK IN PROGRESS
This fork is intended for my personal rewrite/fixup of the flashbot web3.py module.

*Assume that this repository is non-functional regardless of CI status below*

[![CI](https://github.com/N0K0/web3-flashbots/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/N0K0/web3-flashbots/actions/workflows/main.yml)

## TODO:
* Implement signatures
* Make simple example for front/backrunning for example
* Cleanup Types
* Cleanup the web3 module (should be possible to expose )


This library works by injecting a new module in the Web3.py instance, which allows
submitting "bundles" of transactions directly to miners. This is done by also creating
a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends
them to an RPC endpoint which you have specified, which corresponds to `mev-geth`.

## Example

```python
from web3 import Web3, HTTPProvider
from flashbots import flashbot
w3 = Web3(HTTPProvider("http://localhost:8545"))
flashbot(w3)
```

Now the `w3.flashbots.sendBundle` method should be available to you. Look in `examples/demo.py` for usage examples

# Development and testing

Setup and run (mev-)geth with Websocket support:
```
geth --http --http.api eth,net,web3,txpool --syncmode full
```

Install [poetry](https://python-poetry.org/)

Poetry will automatically fix your venv and all packages needed
```
poetry install
```
Tips: PyCharm has a poetry plugin


## Linting
It's advisable to run black with default rules for linting

```
sudo pip install black # Black should be installed with a global entrypoint
black .
```

