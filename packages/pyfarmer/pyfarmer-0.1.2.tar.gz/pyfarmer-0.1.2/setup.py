# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfarmer']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'pyfarmer',
    'version': '0.1.2',
    'description': 'A farmer for your flag farm',
    'long_description': None,
    'author': 'rikyiso01',
    'author_email': '31405152+rikyiso01@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
