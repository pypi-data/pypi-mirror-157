# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auto_flask', 'auto_flask.market']

package_data = \
{'': ['*'], 'auto_flask.market': ['templates/*', 'templates/includes/*']}

install_requires = \
['Flask-Bcrypt>=1.0.1,<2.0.0',
 'Flask-Login>=0.6.1,<0.7.0',
 'Flask-SQLAlchemy>=2.5.1,<3.0.0',
 'Flask-WTF>=1.0.1,<2.0.0',
 'Flask>=2.1.2,<3.0.0',
 'email-validator>=1.2.1,<2.0.0',
 'pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'auto-flask',
    'version': '0.1.1',
    'description': 'flask login register auto',
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
