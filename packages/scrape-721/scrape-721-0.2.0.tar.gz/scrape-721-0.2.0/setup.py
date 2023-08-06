# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scrape_721']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.20.0,<0.21.0',
 'redis>=4.3.4,<5.0.0',
 'typer>=0.4.2,<0.5.0',
 'web3>=5.29.2,<6.0.0']

entry_points = \
{'console_scripts': ['scrape-721 = scrape_721.main:app']}

setup_kwargs = {
    'name': 'scrape-721',
    'version': '0.2.0',
    'description': '"A basic tool for scraping ERC-721 smart contract data"',
    'long_description': '# Example Package\n\nThis is a simple example package. You can use\n[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)\nto write your content.\n',
    'author': 'Corey Bothwell',
    'author_email': 'corey.bothwell@uzh.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
