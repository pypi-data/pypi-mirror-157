# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['news_fetcher']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'click>=8.1.3,<9.0.0',
 'feedparser>=6.0.10,<7.0.0',
 'tortoise-orm[asyncpg,accel]>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'news-fetcher',
    'version': '0.2.0',
    'description': 'Script to fetch news using API and convert to wiki-text',
    'long_description': None,
    'author': 'Artiom Khandamirov',
    'author_email': 't9max@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<=3.11',
}


setup(**setup_kwargs)
