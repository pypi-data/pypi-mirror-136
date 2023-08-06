# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gke_logging']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

extras_require = \
{'asgi': ['starlette>=0.18.0,<0.19.0']}

setup_kwargs = {
    'name': 'gke-logging',
    'version': '0.0.1',
    'description': 'Utilities for interacting with logging facilities in GKE workloads',
    'long_description': None,
    'author': 'Station A',
    'author_email': 'oss@stationa.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
