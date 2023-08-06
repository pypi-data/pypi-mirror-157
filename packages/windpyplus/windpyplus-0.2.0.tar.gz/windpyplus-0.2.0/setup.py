# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['windpyplus',
 'windpyplus.concept',
 'windpyplus.fundamental',
 'windpyplus.info',
 'windpyplus.marketStat',
 'windpyplus.scheduler',
 'windpyplus.stock',
 'windpyplus.stockPool',
 'windpyplus.stockSector',
 'windpyplus.technical',
 'windpyplus.utils']

package_data = \
{'': ['*'], 'windpyplus': ['Scripts/*']}

setup_kwargs = {
    'name': 'windpyplus',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'romepeng',
    'author_email': 'romepeng@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
