# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src',
 'src.tests',
 'src.tests.hypothesis',
 'src.tests.modules',
 'src.tests.modules.package_with',
 'src.tests.modules.package_with.subpackage',
 'src.tests.modules.package_without',
 'src.tests.sqlalchemy',
 'src.utilities',
 'src.utilities.hypothesis',
 'src.utilities.sqlalchemy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dycw-utilities',
    'version': '0.2.0',
    'description': 'Miscellaneous Python utilities',
    'long_description': None,
    'author': 'Derek Wan',
    'author_email': 'd.wan@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
