# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beamer',
 'beamer.models',
 'beamer.tests',
 'beamer.tests.agent',
 'beamer.tests.agent.unit',
 'beamer.tests.contracts']

package_data = \
{'': ['*'], 'beamer': ['data/*', 'data/abi/*', 'data/relayers/*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'prometheus-client>=0.14.1,<0.15.0',
 'python-statemachine>=0.8.0,<0.9.0',
 'structlog>=21.5.0,<22.0.0',
 'web3>=5.24.0,<6.0.0']

entry_points = \
{'console_scripts': ['beamer-agent = beamer.cli:main']}

setup_kwargs = {
    'name': 'beamer-bridge',
    'version': '0.0.1',
    'description': 'Bridging rollups with L1 guaranteed security',
    'long_description': '[![Agent CI](https://github.com/beamer-bridge/beamer/actions/workflows/backend.yml/badge.svg)](https://github.com/beamer-bridge/beamer/actions/workflows/backend.yml)\n[![Frontend CI](https://github.com/beamer-bridge/beamer/actions/workflows/frontend.yml/badge.svg)](https://github.com/beamer-bridge/beamer/actions/workflows/frontend.yml)\n\n# Beamer Bridge\n*Transfer ERC20 assets directly between EVM compatible rollups - with a world class user experience*\n\nBeamer is a protocol to enable users to move tokens from one rollup to another.\nThe user requests a transfer by providing tokens on the source rollup.\nLiquidity providers then fill the request and directly send tokens to the user\non the target rollup.\n\nDocumentation: https://docs.beamerbridge.com\nTestnet frontend: https://testnet.beamerbridge.com\n\n\n## Running an agent from source\n\nPrerequisites: Python 3.9.x and Poetry\n\nClone this repository and enter the virtual environment:\n```\n    poetry shell\n```\n\nInstall the necessary dependencies:\n```\n    poetry install\n```\n\nFinally, still within the virtual environment, run:\n```\n    beamer-agent --keystore-file <keyfile> \\\n                 --password <keyfile-password> \\\n                 --l1-rpc-url <l1-rpc-url> \\\n                 --l2a-rpc-url <source-l2-rpc-url> \\\n                 --l2b-rpc-url <target-l2-rpc-url> \\\n                 --deployment-dir <contract-deployment-dir> \\\n                 --token-match-file <token-match-file>\n```\n\nFor more comprehensive documentation go to [Beamer documenation](https://docs.beamerbridge.com).\n',
    'author': 'Beamer Bridge Team',
    'author_email': 'contact@beamerbridge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.beamerbridge.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
