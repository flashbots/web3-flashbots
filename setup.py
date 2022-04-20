# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flashbots']

package_data = \
{'': ['*']}

install_requires = \
['web3>=5.22.0,<6']

setup_kwargs = {
    'name': 'flashbots',
    'version': '1.0.0',
    'description': 'web3-flashbots.py',
    'long_description': '\nThis library works by injecting a new module in the Web3.py instance, which allows\nsubmitting "bundles" of transactions directly to miners. This is done by also creating\na middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends\nthem to an RPC endpoint which you have specified, which corresponds to `mev-geth`. \nTo apply correct headers we use FlashbotProvider which injects the correct header on post \n\n## Example\n\n```python\nfrom eth_account.signers.local import LocalAccount\nfrom web3 import Web3, HTTPProvider\nfrom flashbots import flashbot\nfrom eth_account.account import Account\nimport os\n\nETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNATURE_KEY"))\n\n\nw3 = Web3(HTTPProvider("http://localhost:8545"))\nflashbot(w3, ETH_ACCOUNT_SIGNATURE)\n```\n\nNow the `w3.flashbots.sendBundle` method should be available to you. Look in `examples/simple.py` for usage examples\n\n# Development and testing\n\nSetup and run (mev-)geth with Websocket support:\n```\ngeth --http --http.api eth,net,web3,txpool --syncmode full\n```\n\nInstall [poetry](https://python-poetry.org/)\n\nPoetry will automatically fix your venv and all packages needed\n```\npoetry install\n```\nTips: PyCharm has a poetry plugin\n\n\n## Linting\nIt\'s advisable to run black with default rules for linting\n\n```\nsudo pip install black # Black should be installed with a global entrypoint\nblack .\n```\n\n',
    'long_description_content_type': 'text/markdown',
    'author': 'Georgios Konstantopoulos',
    'author_email': 'me@gakonst.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
