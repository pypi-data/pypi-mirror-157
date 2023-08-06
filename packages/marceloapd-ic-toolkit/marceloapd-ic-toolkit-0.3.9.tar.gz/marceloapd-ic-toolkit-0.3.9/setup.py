# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['marceloapd_ic_toolkit']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL',
 'boto3',
 'botocore',
 'certifi',
 'click',
 'colorama',
 'distlib',
 'filelock',
 'jmespath',
 'numpy',
 'pandas',
 'pipenv',
 'platformdirs',
 'python-dateutil',
 'pytz',
 's3transfer',
 'six',
 'typer[all]>=0.4.1,<0.5.0',
 'urllib3',
 'virtualenv',
 'virtualenv-clone']

entry_points = \
{'console_scripts': ['ic = marceloapd_ic_toolkit.main:app']}

setup_kwargs = {
    'name': 'marceloapd-ic-toolkit',
    'version': '0.3.9',
    'description': '',
    'long_description': 'toolkit',
    'author': 'Marcelo Assis',
    'author_email': '94455042+marceloapda@users.noreply.github.com',
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
