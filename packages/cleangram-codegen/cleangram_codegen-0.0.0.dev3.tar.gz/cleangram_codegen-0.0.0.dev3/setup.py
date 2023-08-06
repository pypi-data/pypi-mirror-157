# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cleangram_codegen']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'black>=22.3.0,<23.0.0',
 'flake8>=4.0.1,<5.0.0',
 'httpx',
 'isort>=5.10.1,<6.0.0',
 'mypy>=0.961,<0.962',
 'pydantic>=1.9.1,<2.0.0',
 'typer>=0.4.1,<0.5.0']

setup_kwargs = {
    'name': 'cleangram-codegen',
    'version': '0.0.0.dev3',
    'description': 'Code generator for cleangram',
    'long_description': None,
    'author': 'Arwichok',
    'author_email': 'me@arwi.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
