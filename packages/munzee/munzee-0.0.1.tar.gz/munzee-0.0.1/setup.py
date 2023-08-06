# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['munzee']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'munzee',
    'version': '0.0.1',
    'description': 'Python Munzee API wrapper',
    'long_description': '# munzeepy\nPython Munzee API wrapper\n',
    'author': 'MatyiFKBT',
    'author_email': '6183867+MatyiFKBT@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
