# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['villonaco']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'villonaco',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Marco Montanio',
    'author_email': 'mjmontano1@utpl.edu.ec',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
