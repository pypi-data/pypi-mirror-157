# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leonadormida']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'leonadormida',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Danilo',
    'author_email': 'drleon416@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
