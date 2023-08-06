# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyi18n_new', 'pyi18n_new.lib', 'pyi18n_new.models']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pyi18n-new',
    'version': '1.0.2',
    'description': 'Advanced i18n realization',
    'long_description': '# pyi18n',
    'author': 'Daniel Zakharov',
    'author_email': 'gzdan734@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
