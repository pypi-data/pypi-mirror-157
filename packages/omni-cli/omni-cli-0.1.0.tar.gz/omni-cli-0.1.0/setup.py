# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omni_cli']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['omni-cli = omni_cli.main:app']}

setup_kwargs = {
    'name': 'omni-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Omni CLI\n\nThe awesome Omni CLI.\n',
    'author': 'Derrick',
    'author_email': 'derrick@example.com',
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
