# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypi_stub']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'epure',
    'version': '0.1.0',
    'description': 'purest architecture',
    'long_description': None,
    'author': 'nagvalhm',
    'author_email': 'nagvalhm@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
