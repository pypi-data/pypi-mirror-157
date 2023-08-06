# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['port_cloud']

package_data = \
{'': ['*'], 'port_cloud': ['templates/*', 'templates/includes/*']}

install_requires = \
['Flask-Bcrypt>=1.0.1,<2.0.0',
 'Flask-Login>=0.6.1,<0.7.0',
 'Flask-SQLAlchemy>=2.5.1,<3.0.0',
 'Flask-SocketIO>=5.2.0,<6.0.0',
 'Flask-WTF>=1.0.1,<2.0.0',
 'Flask>=2.1.2,<3.0.0',
 'email-validator>=1.2.1,<2.0.0',
 'pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'port-cloud',
    'version': '0.1.1',
    'description': 'port cloud terminal',
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
