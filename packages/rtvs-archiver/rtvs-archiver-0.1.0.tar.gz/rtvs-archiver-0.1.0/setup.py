# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rtvs_archiver']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'aiohttp>=3.8.1,<4.0.0',
 'click>=8.0.3,<9.0.0',
 'lxml>=4.7.1,<5.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['rtvs_archiver = rtvs_archiver.cli:main']}

setup_kwargs = {
    'name': 'rtvs-archiver',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mathew Cohle',
    'author_email': 'mathewcohle@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
