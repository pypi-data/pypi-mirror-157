# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elmarvinflores']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'elmarvinflores',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Marvin Flores',
    'author_email': 'elmarvinflores@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
