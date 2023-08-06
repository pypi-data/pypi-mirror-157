# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['katz']

package_data = \
{'': ['*']}

install_requires = \
['paho-mqtt>=1.6.1,<2.0.0', 'python-osc>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'katz',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kevin Katz',
    'author_email': 'kevcmk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
