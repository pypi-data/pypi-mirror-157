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
    'version': '0.1.1',
    'description': 'An easy-to-use nameko cache',
    'long_description': '# nameko-cache\n\nAn easy-to-use nameko cache\n\nSome code references from repo [nameko-cachetools](https://github.com/santiycr/nameko-cachetools)\n\n# Install\n```shell\npip install nameko-cachelib\n```\n\n# Example\n```python\n\n    class Service:\n        name = "service"\n\n        cached_service = CacheRpcProxy("service")\n\n        @rpc\n        def cached(self, *args, **kwargs):\n            return self.cached_service.some_method(*args, **kwargs)\n\n```\n\n# TODO list\n## memory cache\n\n## single flight\n\n## redis cache\n\n\n',
    'author': 'Pony Ma',
    'author_email': 'mtf201013@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ma-pony/nameko-cache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
