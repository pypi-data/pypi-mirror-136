# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dh2vrml']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'x3d>=4.0.47,<5.0.0',
 'xmlschema>=1.9.2,<2.0.0']

entry_points = \
{'console_scripts': ['dh2vrml = dh2vrml.cli:main']}

setup_kwargs = {
    'name': 'dh2vrml',
    'version': '0.1.0',
    'description': 'Library and CLI tool to convert Denavit–Hartenberg parameters to an X3D model',
    'long_description': None,
    'author': 'Jasper Chan',
    'author_email': 'jasperchan515@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
