# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repoaudit']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'python-debian>=0.1.44,<0.2.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['repoaudit = repoaudit:main']}

setup_kwargs = {
    'name': 'repoaudit',
    'version': '0.1.0',
    'description': 'CLI to validate yum/apt repositories',
    'long_description': "# repoaudit\n\nA tool for validating apt and yum repositories.\n\n## Installation\n\nFirst install poetry:\n\nhttps://python-poetry.org/docs/#installation\n\nThen run `poetry install` to install repoaudit's dependencies.\n\n### Development\n\nTo load the poetry shell:\n\n```\npoetry shell\nrepoaudit\n```\n\nAltenatively you can run:\n\n```\npoetry run repoaudit\n```\n\n## Usage\n\nTo get a list of commands and options:\n\n```\nrepoaudit --help\n```\n\n### Examples\n\n```\n# validate all distros of azure-cli apt repo\nrepoaudit apt https://packages.microsoft.com/repos/azure-cli/\n\n# validate only focal and bionic distros of azure-cli apt repo\nrepoaudit apt --dist focal --dist bionic https://packages.microsoft.com/repos/azure-cli/\n\n# validate azurecore repo\nrepoaudit yum https://packages.microsoft.com/yumrepos/azurecore/\n\n# validate all nested yumrepos\nrepoaudit yum -r https://packages.microsoft.com/yumrepos/\n```\n",
    'author': None,
    'author_email': None,
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
