# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yanniszark_common']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'yanniszark-common',
    'version': '0.1.48',
    'description': 'Idiomatic, reusable code for a bunch of use-cases.',
    'long_description': None,
    'author': 'Yannis Zarkadas',
    'author_email': 'yanniszark@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
