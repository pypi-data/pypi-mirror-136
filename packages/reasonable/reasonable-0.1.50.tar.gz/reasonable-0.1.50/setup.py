# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reasonable']

package_data = \
{'': ['*']}

install_requires = \
['brickschema>=0.5,<0.6']

setup_kwargs = {
    'name': 'reasonable',
    'version': '0.1.50',
    'description': "Python interface to 'reasonable', a Datalog implementation of the OWL 2 RL profile",
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@mines.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
