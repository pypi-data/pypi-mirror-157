# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cougar_log']

package_data = \
{'': ['*']}

install_requires = \
['Fabric>=2.7.0,<3.0.0',
 'click-spinner>=0.1.10,<0.2.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['cougar-log = cougar_log.main:app']}

setup_kwargs = {
    'name': 'cougar-log',
    'version': '0.1.3',
    'description': '',
    'long_description': '# Cougar Log\n\n**Cougar Log is a CLI for rapidly converting and visualizing .wpilog files!**\n\nSee the following page for a guide on creating these files inside of an FRC robotics project:\n\n[https://docs.wpilib.org/en/stable/docs/software/telemetry/datalog.html](https://docs.wpilib.org/en/stable/docs/software/telemetry/datalog.html)\n\n## Quickstart\n\n### Installation\n\nRun the following to install `cougar-log` using pip:\n\n```\npip install cougar-log\n```\n\n### Basic Usage Examples\n\n_See the documentation below this section for more specific capabilities of this CLI._\n\nIn this example, we have a file in our current directory called `my_data_log.wpilog`.\n\n#### Converting to CSV\n\n```\ncougar-log convert -i my_data_log.wpilog\n```\n\n_or, to convert any file in the given folder:_\n\n```\ncougar-log convert -i .\n```\n\n#### Displaying as a Table\n\n```\ncougar-log table -i my_data_log.wpilog\n```\n\n#### Graphing Data\n\n```\ncougar-log graph -i my_data_log.wpilog\n```\n\n#### Filtering\n\nAny of these commands can be used with a filter flag (`-f/--filter`) in order to select only the entries that have that name.\n\nUse the table option to see the names of all of the log entries.\n\n```\ncougar-log graph -i my_data_log.wpilog -f /temps/drive\n```\n\n#### Downloading Files from a Robot\n\nReplace XX.XX with your team number in that format.\n\n_Note: this command has a multitude of options available._\n\n```\ncougar-log download --host "10.XX.XX.2"\n```\n\n## Documentation\n\nClick the link below to visit the documentation:\n\n[frc2539.github.io/cougar-log](https://frc2539.github.io/cougar-log)',
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
