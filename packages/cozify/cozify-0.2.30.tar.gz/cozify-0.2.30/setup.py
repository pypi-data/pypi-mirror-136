# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cozify', 'cozify.test']

package_data = \
{'': ['*']}

install_requires = \
['absl-py>=1.0.0,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'cozify',
    'version': '0.2.30',
    'description': 'Unofficial Python3 API bindings for the (unpublished) Cozify API.',
    'long_description': None,
    'author': 'Artanicus',
    'author_email': 'artanicus@nocturnal.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
