# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['radiotherapyai']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['radiotherapyai = radiotherapyai.__main__:app',
                     'rtai = radiotherapyai.__main__:app']}

setup_kwargs = {
    'name': 'radiotherapyai',
    'version': '0.1.0',
    'description': 'AI assisted treatments accessible to all',
    'long_description': None,
    'author': 'Simon Biggs',
    'author_email': 'simon.biggs@radiotherapy.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
