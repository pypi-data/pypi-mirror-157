# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = \
['lark>=0.11.3,<0.12.0', 'wizwalker>=1.0.0', 'loguru', 'asyncio']

setup_kwargs = {
    'name': 'wiznavigator',
    'version': '0.0.1',
    'description': 'A library for navigating between zones and worlds using WizWalker',
    'long_description': '',
    'author': 'wizBots',
    'author_email': '',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': find_packages(),
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}

setup(**setup_kwargs)
