# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chris',
 'chris.utils',
 'chris.utils.enum',
 'chris.utils.env',
 'chris.utils.io']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'chris-utils',
    'version': '0.1.1',
    'description': 'Personal Python Utilities',
    'long_description': '# Chris Utils\n\nPersonal utilities for Python projects.\n',
    'author': 'Chris Gregory',
    'author_email': 'christopher.b.gregory@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gregorybchris/chris-utils',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
