# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gator', 'gator.models', 'gator.schemas']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow-enum>=1.5.1,<2.0.0',
 'marshmallow>=3.17.0,<4.0.0',
 'mongoengine>=0.20']

setup_kwargs = {
    'name': 'gator-models',
    'version': '1.1.2',
    'description': 'MongoDB models for Gator API',
    'long_description': '# gator-models\nMongoDB models for Gator API\n\n## Package manager\nGator-models uses the [poetry](https://python-poetry.org/) package manager to manage its dependencies. To install the dependencies, run the following command:\n```\npoetry install\n```\nSee the [poetry](https://python-poetry.org/) documentation for more information and\ninstallation instructions.\n\n## Tools\n\n#### Linting the codebase\nFor detecting code quality and style issues, run\n```\nflake8\n```\nFor checking compliance with Python docstring conventions, run\n```\npydocstyle\n```\n\n**NOTE**: these tools will not fix any issues, but they can help you identify potential problems.\n\n\n#### Formatting the codebase\nFor automatically formatting the codebase, run\n```\nautopep8 --in-place --recursive .\n```\nFor more information on this command, see the [autopep8](https://pypi.python.org/pypi/autopep8) documentation.\n\nFor automatically sorting imports, run\n```\nisort .\n```',
    'author': 'Shon Verch',
    'author_email': 'verchshon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
