# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['w3ezpz']

package_data = \
{'': ['*']}

install_requires = \
['web3>=5.27.0,<6.0.0']

setup_kwargs = {
    'name': 'w3ezpz',
    'version': '0.0.1a0',
    'description': 'web 3 ezpz',
    'long_description': None,
    'author': 'killingtime',
    'author_email': 'killingtime-sc@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
