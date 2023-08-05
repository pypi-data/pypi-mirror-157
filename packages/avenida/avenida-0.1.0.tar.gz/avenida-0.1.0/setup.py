# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avenida']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'avenida',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ivanna Añazco',
    'author_email': 'ivanna_ao97@outlook.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
