# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskcluster_inspect',
 'taskcluster_inspect.console',
 'taskcluster_inspect.console.commands']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=0.8.1,<0.9.0',
 'petl>=1.7.9,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'taskcluster>=44.13.6,<45.0.0']

entry_points = \
{'console_scripts': ['tc-inspect = '
                     'taskcluster_inspect.console.application:cli']}

setup_kwargs = {
    'name': 'taskcluster-inspect',
    'version': '0.2.0',
    'description': 'A simple command line tool for inspecting Taskcluster state.',
    'long_description': None,
    'author': 'Andrew Halberstadt',
    'author_email': 'ahal@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
