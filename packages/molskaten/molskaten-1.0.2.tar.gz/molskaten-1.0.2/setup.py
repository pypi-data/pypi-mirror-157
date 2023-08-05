# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['molskaten']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4,<5']}

setup_kwargs = {
    'name': 'molskaten',
    'version': '1.0.2',
    'description': 'A (forked) python wrapper for the skolmaten service.',
    'long_description': None,
    'author': 'granis',
    'author_email': 'granis@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/granis/skolmaten-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
