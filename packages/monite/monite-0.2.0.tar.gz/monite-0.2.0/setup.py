# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monite']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'monite',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
