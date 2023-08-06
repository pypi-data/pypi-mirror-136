# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avtocod',
 'avtocod.methods',
 'avtocod.session',
 'avtocod.types',
 'avtocod.types.profile',
 'avtocod.types.review']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'contextvars>=2.4,<3.0', 'pydantic>=1.8.2,<1.9.0']

setup_kwargs = {
    'name': 'avtocod',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Fom123',
    'author_email': 'gamemode1.459@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
