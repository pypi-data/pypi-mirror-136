# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythin']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pythin',
    'version': '0.1.0',
    'description': 'Simpler Python',
    'long_description': None,
    'author': 'WhatDoWeDoNow',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
