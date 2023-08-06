# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gloomhaven']

package_data = \
{'': ['*'], 'gloomhaven': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'PyYAML>=6.0,<7.0']

extras_require = \
{'analyze': ['dask[distributed]>=2022.6.1,<2023.0.0',
             'matplotlib>=3.5.2,<4.0.0',
             'pandas>=1.4.3,<2.0.0',
             'jupyter>=1.0.0,<2.0.0',
             'dictdiffer>=0.9.0,<0.10.0']}

setup_kwargs = {
    'name': 'gloomhaven',
    'version': '1.0.0',
    'description': 'Probability evaluation of Gloomhaven attack modifier decks',
    'long_description': None,
    'author': 'Zachary Coleman',
    'author_email': 'zacharywcoleman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
