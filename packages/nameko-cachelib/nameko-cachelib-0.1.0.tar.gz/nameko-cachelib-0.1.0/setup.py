# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nameko_cachelib']

package_data = \
{'': ['*']}

install_requires = \
['nameko==3.0.0.rc11']

setup_kwargs = {
    'name': 'nameko-cachelib',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Pony Ma',
    'author_email': 'mtf201013@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
