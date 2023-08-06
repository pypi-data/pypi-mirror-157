# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['utilicity', 'utilicity.items']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'utilicity',
    'version': '0.2.0',
    'description': 'Utility libs for Python3.',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/icaine/utilicity',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
