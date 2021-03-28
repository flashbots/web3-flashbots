
This library works by injecting a new module in the Web3.py instance, which allows
submitting "bundles" of transactions directly to miners. This is done by also creating
a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends
them to an RPC endpoint which you have specified, which corresponds to `mev-geth`. 
To apply correct headers we use FlashbotProvider which injects the correct header on post 

## Example

```python
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from flashbots import flashbot
from eth_account.account import Account
import os

ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNATURE_KEY"))


w3 = Web3(HTTPProvider("http://localhost:8545"))
flashbot(w3, ETH_ACCOUNT_SIGNATURE)
```

Now the `w3.flashbots.sendBundle` method should be available to you. Look in `examples/simple.py` for usage examples

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

