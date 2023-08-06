# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['utilities', 'utilities.hypothesis', 'utilities.sqlalchemy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dycw-utilities',
    'version': '0.2.1',
    'description': 'Miscellaneous Python utilities',
    'long_description': None,
    'author': 'Derek Wan',
    'author_email': 'd.wan@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
