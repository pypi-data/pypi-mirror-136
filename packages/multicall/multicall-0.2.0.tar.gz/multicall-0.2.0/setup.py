# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multicall']

package_data = \
{'': ['*']}

install_requires = \
['web3>=5.26.0,<6.0.0']

setup_kwargs = {
    'name': 'multicall',
    'version': '0.2.0',
    'description': 'aggregate results from multiple ethereum contract calls',
    'long_description': None,
    'author': 'banteg',
    'author_email': 'banteeg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
