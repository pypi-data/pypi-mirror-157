# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysubparser',
 'pysubparser.classes',
 'pysubparser.cleaners',
 'pysubparser.parsers',
 'pysubparser.writers']

package_data = \
{'': ['*']}

install_requires = \
['unidecode>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'pysub-parser',
    'version': '1.5.0',
    'description': 'Utility to extract the contents of a subtitle file',
    'long_description': None,
    'author': 'Fede Calendino',
    'author_email': 'fede@calendino.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
