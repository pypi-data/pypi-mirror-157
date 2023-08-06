# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anahita']

package_data = \
{'': ['*']}

install_requires = \
['flatdict>=4.0.1,<5.0.0', 'wikitextparser>=0.49.2,<0.50.0']

setup_kwargs = {
    'name': 'anahita',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Vahid Shahrivari',
    'author_email': 'v.shahrivari@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
