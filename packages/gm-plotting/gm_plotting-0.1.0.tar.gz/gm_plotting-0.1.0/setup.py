# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gm_plotting']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'googlemaps>=4.6.0,<5.0.0',
 'numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'gm-plotting',
    'version': '0.1.0',
    'description': 'Tools for overlaying plots on Google Maps',
    'long_description': None,
    'author': 'Alex Dewar',
    'author_email': 'a.dewar@imperial.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BrainsOnBoard/python-gm-plotting',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
