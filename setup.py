# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["flashbots"]

package_data = {"": ["*"]}

install_requires = ["web3>=5.22.0,<6"]

setup_kwargs = {
    "name": "flashbots",
    "version": "1.0.1-1",
    "description": "web3-flashbots.py",
    "long_description": 'This library works by injecting flashbots as a new module in the Web3.py instance, which allows submitting "bundles" of transactions directly to miners. This is done by also creating a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends them to an RPC endpoint which you have specified, which corresponds to `mev-geth`.\n\nTo apply correct headers we use the `flashbot` method which injects the correct header on POST.\n\n## Quickstart\n\n```python\nfrom eth_account.signers.local import LocalAccount\nfrom web3 import Web3, HTTPProvider\nfrom flashbots import flashbot\nfrom eth_account.account import Account\nimport os\n\nETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNATURE_KEY"))\n\n\nw3 = Web3(HTTPProvider("http://localhost:8545"))\nflashbot(w3, ETH_ACCOUNT_SIGNATURE)\n```\n\nNow the `w3.flashbots.sendBundle` method should be available to you. Look in [examples/simple.py](./examples/simple.py) for usage examples.\n\n### Goerli\n\nTo use goerli, add the goerli relay RPC to the `flashbot` function arguments.\n\n```python\nflashbot(w3, ETH_ACCOUNT_SIGNATURE, "https://relay-goerli.flashbots.net")\n```\n\n## Development and testing\n\nInstall [poetry](https://python-poetry.org/)\n\nPoetry will automatically fix your venv and all packages needed.\n\n```sh\npoetry install\n```\n\nTips: PyCharm has a poetry plugin\n\n## Simple Goerli Example\n\nSee [examples/simple.py](./examples/simple.py) for environment variable definitions.\n\n```sh\npoetry shell\nETH_SENDER_KEY=<sender_private_key> \\nPROVIDER_URL=https://eth-goerli.alchemyapi.io/v2/<alchemy_key> \\nETH_SIGNER_KEY=<signer_private_key> \\npython examples/simple.py\n```\n\n## Linting\n\nIt\'s advisable to run black with default rules for linting\n\n```sh\nsudo pip install black # Black should be installed with a global entrypoint\nblack .\n```',
    "long_description_content_type": "text/markdown",
    "author": "Georgios Konstantopoulos",
    "author_email": "me@gakonst.com",
    "maintainer": "zeroXbrock",
    "maintainer_email": None,
    "url": "https://github.com/flashbots/web3-flashbots",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.9,<4.0",
}


setup(**setup_kwargs)
