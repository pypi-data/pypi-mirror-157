# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vim_session_manager']

package_data = \
{'': ['*']}

install_requires = \
['inquirer>=2.9.2,<3.0.0', 'result>=0.7.0,<0.8.0', 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['vsm = vim_session_manager.__main__:main']}

setup_kwargs = {
    'name': 'vim-session-manager',
    'version': '0.1.1',
    'description': 'A small python program for managing vim sessions',
    'long_description': None,
    'author': 'Matt Williams',
    'author_email': 'matt.k.williams@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10.1,<4.0.0',
}


setup(**setup_kwargs)
