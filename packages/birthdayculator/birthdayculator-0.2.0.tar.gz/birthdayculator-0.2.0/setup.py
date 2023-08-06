# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['birthdayculator']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'birthdayculator',
    'version': '0.2.0',
    'description': 'A thin and extremely specialised wrapper around luxon for calculating birthday info from a birth date. Ported from npm library',
    'long_description': None,
    'author': 'Rick Cooper',
    'author_email': 'rcoops84@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
