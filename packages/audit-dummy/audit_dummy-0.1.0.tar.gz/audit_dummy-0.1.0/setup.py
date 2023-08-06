# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['audit_dummy']

package_data = \
{'': ['*']}

install_requires = \
['graphene==3.0']

setup_kwargs = {
    'name': 'audit-dummy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'LukeBoyer',
    'author_email': 'boyer.l@husky.neu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
