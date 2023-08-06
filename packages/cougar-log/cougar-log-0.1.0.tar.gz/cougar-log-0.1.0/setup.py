# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cougar_log']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.6.0,<23.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['cougar-log = cougar_log.main:app']}

setup_kwargs = {
    'name': 'cougar-log',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Cougar-Log\n\nA cli for interacting with wpilib log files.\n',
    'author': 'Weaver Goldman',
    'author_email': 'we.goldm@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
