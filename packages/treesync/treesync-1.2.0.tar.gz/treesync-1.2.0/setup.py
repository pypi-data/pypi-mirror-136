# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['treesync',
 'treesync.bin',
 'treesync.bin.treesync',
 'treesync.bin.treesync.commands']

package_data = \
{'': ['*']}

install_requires = \
['pathlib-tree>=2.1,<3.0']

entry_points = \
{'console_scripts': ['treesync = treesync.bin.treesync.main:main']}

setup_kwargs = {
    'name': 'treesync',
    'version': '1.2.0',
    'description': 'Utilitiies to use rsync for whole trees',
    'long_description': None,
    'author': 'Ilkka Tuohela',
    'author_email': 'hile@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
