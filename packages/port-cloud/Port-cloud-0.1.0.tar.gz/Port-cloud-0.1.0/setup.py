# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['port_cloud']

package_data = \
{'': ['*'], 'port_cloud': ['templates/*', 'templates/includes/*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'port-cloud',
    'version': '0.1.0',
    'description': 'Terminal port cloud  ',
    'long_description': None,
    'author': 'ported',
    'author_email': 'shahinmondal42bd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
