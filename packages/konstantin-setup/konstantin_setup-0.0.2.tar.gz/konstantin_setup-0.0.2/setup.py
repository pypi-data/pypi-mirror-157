# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['konstantin_setup']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'konstantin-setup',
    'version': '0.0.2',
    'description': 'Скрипты установки',
    'long_description': None,
    'author': 'Konstantin-Dudersky',
    'author_email': 'Konstantin.Dudersky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
