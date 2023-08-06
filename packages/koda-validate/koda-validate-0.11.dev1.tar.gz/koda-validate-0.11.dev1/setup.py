# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['koda_validate']

package_data = \
{'': ['*']}

install_requires = \
['koda==0.11.0']

setup_kwargs = {
    'name': 'koda-validate',
    'version': '0.11.dev1',
    'description': '',
    'long_description': None,
    'author': 'Keith Philpott',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
