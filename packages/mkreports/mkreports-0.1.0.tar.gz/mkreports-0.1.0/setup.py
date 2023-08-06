# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkreports', 'mkreports.md']

package_data = \
{'': ['*'], 'mkreports': ['.pytest_cache/*', '.pytest_cache/v/cache/*']}

install_requires = \
['PyYAML>=6.0',
 'anytree>=2.8.0,<3.0.0',
 'deepmerge>=0.3.0',
 'immutabledict>=2.2.1',
 'intervaltree>=3.1.0,<4.0.0',
 'mdutils>=1.3.1',
 'mkdocs-material>=7.3.6',
 'mkdocs>=1.2.3',
 'more-itertools>=8.12.0,<9.0.0',
 'plotly>=5.5.0,<6.0.0',
 'pytest>=6.2.5',
 'python-frontmatter>=1.0.0',
 'tabulate>=0.8.9',
 'typer>=0.4.0,<0.5.0',
 'typing-extensions<=3.11']

extras_require = \
{':python_version >= "3.7" and python_version < "4.0"': ['mkdocstrings>=0.17.0,<0.18.0']}

setup_kwargs = {
    'name': 'mkreports',
    'version': '0.1.0',
    'description': 'Creating static reports from python using mkdocs',
    'long_description': None,
    'author': 'Holger Hoefling',
    'author_email': 'hhoeflin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
