# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shinkansen']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=37.0.3,<38.0.0', 'jwcrypto>=1.3.1,<2.0.0']

setup_kwargs = {
    'name': 'python-shinkansen',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Leonardo Soto M.',
    'author_email': 'leo.soto@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
