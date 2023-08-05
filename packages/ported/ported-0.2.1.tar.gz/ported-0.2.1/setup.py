# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ported']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'ported',
    'version': '0.2.1',
    'description': 'port forword website for any ',
    'long_description': None,
    'author': 'ported',
    'author_email': 'shahinmondal42bd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
