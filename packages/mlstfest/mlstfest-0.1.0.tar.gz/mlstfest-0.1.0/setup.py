# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlstfest']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['mlstfest = mlstfest.main:app']}

setup_kwargs = {
    'name': 'mlstfest',
    'version': '0.1.0',
    'description': 'mlstfest can assign a strain type to novel microbial WGS data',
    'long_description': None,
    'author': 'henningonsbring',
    'author_email': 'henning.onsbring@scilifelab.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
