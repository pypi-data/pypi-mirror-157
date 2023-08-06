# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ankr']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'pyhumps>=3.7.2,<4.0.0', 'web3>=5.29.2,<6.0.0']

setup_kwargs = {
    'name': 'ankr-sdk',
    'version': '0.1.1',
    'description': "Compact Python library for interacting with Ankr's Advanced APIs.",
    'long_description': None,
    'author': 'Roman Fasakhov',
    'author_email': 'romanfasakhov@ankr.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
