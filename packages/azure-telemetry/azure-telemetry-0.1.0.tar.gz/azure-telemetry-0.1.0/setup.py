# -*- coding: utf-8 -*-
from setuptools import setup
import os

packages = \
['azure_telemetry']

package_data = \
{'': ['*']}

DIRECTORY = os.path.dirname(__file__)
READ_ME = open(os.path.join(DIRECTORY, "README.txt")).read()

install_requires = \
['azure-mgmt-datalake-analytics>=0.6.0,<0.7.0',
 'azure-mgmt-monitor>=3.0.0,<4.0.0',
 'msrestazure>=0.6.4,<0.7.0',
 'opencensus-ext-azure>=1.1.0,<2.0.0',
 'opencensus-ext-requests>=0.7.6,<0.8.0']

setup_kwargs = {
    'name': 'azure-telemetry',
    'version': '0.1.0',
    'description': '',
    'long_description': READ_ME,
    'author': 'RajamannarAanjaram',
    'author_email': 'rajamannaraanjaram@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
