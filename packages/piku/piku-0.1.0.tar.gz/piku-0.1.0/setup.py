# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['piku', 'piku.commands']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['piku = piku.main:main']}

setup_kwargs = {
    'name': 'piku',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Piku\nA small command line utility for managing CircuitPython projects\n',
    'author': 'Mark Raleson',
    'author_email': 'markraleson@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mraleson/rag.git',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
