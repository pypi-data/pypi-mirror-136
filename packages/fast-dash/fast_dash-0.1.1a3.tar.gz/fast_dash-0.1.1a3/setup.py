# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_dash', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'dash-bootstrap-components>=1.0.2,<2.0.0',
 'dash>=2.1.0,<3.0.0',
 'plotly>=5.5.0,<6.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'livereload>=2.6.3,<3.0.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'fast-dash',
    'version': '0.1.1a3',
    'description': 'Create input-output web applications and user interfaces using Plotly Dash lightning fast..',
    'long_description': '# Fast Dash\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/fast_dash">\n    <img src="https://img.shields.io/pypi/v/fast_dash.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/dkedar7/fast_dash/actions">\n    <img src="https://github.com/dkedar7/fast_dash/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<a href="https://fast-dash.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/fast-dash/badge/?version=latest" alt="Documentation Status">\n</a>\n\n</p>\n\n\nCreate input-output web applications and user interfaces using Plotly Dash lightning fast.\n\n\n* Free software: MIT\n* Documentation: <https://fast-dash.readthedocs.io>\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Kedar Dabhadkar',
    'author_email': 'kdabhadk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dkedar7/fast_dash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
