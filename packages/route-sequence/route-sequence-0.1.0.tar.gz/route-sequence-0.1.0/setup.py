# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['route_sequence']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'route-sequence',
    'version': '0.1.0',
    'description': 'A sequence number range from AA0000 to ZZ9999',
    'long_description': None,
    'author': 'Kim Timothy Engh',
    'author_email': 'kte@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
