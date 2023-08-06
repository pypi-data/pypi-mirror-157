# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enil', 'enil.akad', 'enil.linepy']

package_data = \
{'': ['*']}

install_requires = \
['PyQRCode>=1.2.1,<2.0.0',
 'httplib2>=0.20.4,<0.21.0',
 'httpx>=0.23.0,<0.24.0',
 'hyper>=0.7.0,<0.8.0',
 'lesting.api.client>=0.1.1,<0.2.0',
 'pycryptodome>=3.15.0,<4.0.0',
 'python-axolotl-curve25519>=0.4.1,<0.5.0',
 'requests>=2.28.0,<3.0.0',
 'rsa>=4.8,<5.0',
 'thrift>=0.16.0,<0.17.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'enil',
    'version': '0.2.2',
    'description': '',
    'long_description': None,
    'author': ' ',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
