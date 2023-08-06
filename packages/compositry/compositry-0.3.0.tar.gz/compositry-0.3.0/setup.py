# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['compositry']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4,<0.5']

setup_kwargs = {
    'name': 'compositry',
    'version': '0.3.0',
    'description': 'A tiny library inspired by frontend frameworks to experiment with the idea of composable automation scripts reduced to functions.',
    'long_description': '# Compositry\n\nA tiny library inspired by frontend frameworks to experiment with the idea of composable automation scripts reduced to functions.\n',
    'author': 'Dense Reptile',
    'author_email': '80247368+DenseReptile@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
