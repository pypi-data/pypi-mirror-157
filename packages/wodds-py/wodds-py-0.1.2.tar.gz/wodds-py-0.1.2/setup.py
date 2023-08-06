# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wodds_py']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.0,<2.0.0', 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'wodds-py',
    'version': '0.1.2',
    'description': 'Whisker Odds. Tukey inspired letter-values',
    'long_description': None,
    'author': 'Alex Hallam',
    'author_email': 'alexhallam6.28@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~alexhallam/wodds-py/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
