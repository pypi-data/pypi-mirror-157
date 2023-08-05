# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ctrlmaniac', 'ctrlmaniac.rps']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['ctrlmaniac.rps = ctrlmaniac.rsp.main:play']}

setup_kwargs = {
    'name': 'ctrlmaniac.rps',
    'version': '1.1.0',
    'description': 'The famous Rock Paper Scissors game written in python',
    'long_description': None,
    'author': 'Davide Di Criscito',
    'author_email': 'davide.dicriscito@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
