# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pynbcache']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 's3fs>=2022.5.0,<2023.0.0',
 'tables>=3.7.0,<4.0.0']

setup_kwargs = {
    'name': 'pynbcache',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Julian Stier',
    'author_email': 'julian.stier@uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
