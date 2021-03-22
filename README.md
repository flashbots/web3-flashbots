# web3-flashbots

This library works by injecting a new module in the Web3.py instance, which allows
submitting "bundles" of transactions directly to miners. This is done by also creating
a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends
them to an RPC endpoint which you have specified, which corresponds to `mev-geth`.

## Example

```python
from web3 import Web3, WebsocketProvider
from web3_flashbots import flashbot
w3 = Web3(WebsocketProvider("ws://localhost:8546"))
flashbot(w3, flashbots_key_id="MY_API_ID", flashbots_secret="MY_API_SECRET")
```

Now the `w3.flashbots.sendBundle` method should be available to you. Look in `examples/demo.py` for usage examples

# Development and testing

Setup and run (mev-)geth with Websocket support:
```
geth --ws --ws.api eth,net,web3,txpool --syncmode full
```

Install [poetry](https://python-poetry.org/)

Poetry will automatically fix your venv and all packages needed
```
poetry install
```

Tips: PyCharm has a poetry plugin too
