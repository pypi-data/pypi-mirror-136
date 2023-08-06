# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pocketchemist',
 'pocketchemist.cli',
 'pocketchemist.modules',
 'pocketchemist.processors',
 'pocketchemist.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.22.0,<2.0.0',
 'scipy>=1.7.3,<2.0.0']

extras_require = \
{'torch': ['torch>=1.10,<2.0']}

entry_points = \
{'console_scripts': ['pc = pocketchemist.cli:main']}

setup_kwargs = {
    'name': 'pocketchemist',
    'version': '0.1.1',
    'description': 'Software for the analysis of spectra and molecules',
    'long_description': None,
    'author': 'J Lorieau',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
