# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['apibara', 'apibara.application', 'apibara.indexer', 'apibara.starknet']

package_data = \
{'': ['*']}

install_requires = \
['aiochannel>=1.1.1,<2.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'backoff>=2.1.2,<3.0.0',
 'click-help-colors>=0.9.1,<0.10.0',
 'click>=8.1.3,<9.0.0',
 'eth-hash[pysha3]>=0.3.2,<0.4.0',
 'grpcio-tools>=1.47.0,<2.0.0',
 'grpcio>=1.47.0,<2.0.0']

entry_points = \
{'console_scripts': ['apibara = apibara.cli:cli']}

setup_kwargs = {
    'name': 'apibara',
    'version': '0.2.0',
    'description': 'Apibara cliend SDK. Build web3-powered applications.',
    'long_description': None,
    'author': 'Francesco Ceccon',
    'author_email': 'francesco@apibara.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
