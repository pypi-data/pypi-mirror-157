# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fintech_fraud_dao_hashing']

package_data = \
{'': ['*']}

install_requires = \
['bitarray>=2.5.1,<3.0.0', 'mmh3>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'fintech-fraud-dao-hashing',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Ben Walton',
    'author_email': 'ben@unit21.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
