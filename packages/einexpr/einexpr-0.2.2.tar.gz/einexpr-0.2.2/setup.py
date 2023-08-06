# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['einexpr']

package_data = \
{'': ['*']}

install_requires = \
['lark>=1.1.2,<2.0.0', 'numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'einexpr',
    'version': '0.2.2',
    'description': '',
    'long_description': None,
    'author': 'IsaacBreen',
    'author_email': '57783927+IsaacBreen@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
