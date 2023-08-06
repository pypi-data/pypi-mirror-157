# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_smsify']

package_data = \
{'': ['*']}

install_requires = \
['anyascii>=0.3.1,<0.4.0']

setup_kwargs = {
    'name': 'py-smsify',
    'version': '0.1.0',
    'description': 'Python library for creating GSM-7 compatible messages',
    'long_description': '',
    'author': 'Simon Wissotsky',
    'author_email': 'Wissotsky@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
