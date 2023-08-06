# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['laproxy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'laproxy',
    'version': '1.0.0',
    'description': 'An easy proxy to setup',
    'long_description': None,
    'author': 'Riccardo Isola',
    'author_email': 'riky.isola@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
