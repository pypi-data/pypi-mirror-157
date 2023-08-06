# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbc_influxdb']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'influxdb-client[extra]>=1.29.1,<2.0.0',
 'pandas>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'dbc-influxdb',
    'version': '0.2.0',
    'description': 'Database communication: show, download and upload data. Works with InfluxDB 2.x.',
    'long_description': None,
    'author': 'holukas',
    'author_email': 'lukas.hoertnagl@usys.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
