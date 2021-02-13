# web3-flashbots

This library works by injecting a new module in the Web3.py instance, which allows
submitting "bundles" of transactions directly to miners. This is done by also creating
a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends
them to an RPC endpoint which you have specified, which corresponds to `mev-geth`.

## Example

```python
from web3 import Web3, HTTPProvider
from web3_flashbots import flashbot
w3 = Web3(HTTPProvider("http://localhost:8545"))
flashbot(w3, flashbots_key_id="MY_API_ID", flashbots_secret="MY_API_SECRET", flashbots_url="http://localhost:8545")
```

Now the `w3.flashbots.sendBundle` method should be available to you. Look in `examples/demo.py` for usage examples

# Test

1. Clone and run mev-geth as instructed in the link
2. `PYTHONPATH=`pwd` && python examples/demo.py`
