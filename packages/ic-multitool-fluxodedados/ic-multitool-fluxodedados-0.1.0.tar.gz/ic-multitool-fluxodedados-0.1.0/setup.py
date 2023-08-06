# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ic_multitool_fluxodedados']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'pandas', 'pymysql', 'typer[all]>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['ic = ic_multitool_fluxodedados.main:app']}

setup_kwargs = {
    'name': 'ic-multitool-fluxodedados',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Marcelo Assis',
    'author_email': '94455042+marceloapda@users.noreply.github.com',
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
