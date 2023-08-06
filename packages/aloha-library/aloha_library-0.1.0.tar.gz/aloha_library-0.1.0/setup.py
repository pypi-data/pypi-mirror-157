# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aloha_library', 'aloha_library.schemas']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'aloha-library',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Jeff',
    'author_email': 'jeff.we.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
