# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hmp_aviel']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.12.0,<3.0.0',
 'Sphinx>=4.0.0,<5.0.0',
 'black>=22.3.0,<23.0.0',
 'click>=8.1.3,<9.0.0',
 'codecov>=2.1.12,<3.0.0',
 'coverage[toml]>=6.4.1,<7.0.0',
 'desert>=2020.11.18,<2021.0.0',
 'flake8-bandit>=3.0.0,<4.0.0',
 'flake8-black>=0.3.3,<0.4.0',
 'flake8-bugbear>=22.6.22,<23.0.0',
 'flake8-import-order>=0.18.1,<0.19.0',
 'flake8>=4.0.1,<5.0.0',
 'marshmallow>=3.17.0,<4.0.0',
 'mypy>=0.961,<0.962',
 'pre-commit>=2.19.0,<3.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'requests>=2.28.0,<3.0.0',
 'sphinx-autodoc-typehints>=1.17,<2.0',
 'typeguard>=2.13.3,<3.0.0',
 'types-requests>=2.28.0,<3.0.0']

entry_points = \
{'console_scripts': ['hmp-aviel = hmp_aviel.console:main']}

setup_kwargs = {
    'name': 'hmp-aviel',
    'version': '0.1.0',
    'description': '',
    'long_description': 'None',
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
