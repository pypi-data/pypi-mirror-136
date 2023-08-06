# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peasy_logs', 'peasy_logs.tests']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'peasy-logs',
    'version': '0.1.0',
    'description': 'Easily ship you logs from functions to various connectors!',
    'long_description': None,
    'author': 'larsheinen',
    'author_email': 'larsheinen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
