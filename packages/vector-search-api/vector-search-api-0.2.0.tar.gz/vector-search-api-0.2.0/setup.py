# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vector_search_api',
 'vector_search_api.exceptions',
 'vector_search_api.helper',
 'vector_search_api.searcher',
 'vector_search_api.vectorizer']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.0.0,<2.0.0', 'pydantic>=1.0.0,<2.0.0', 'tqdm>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'vector-search-api',
    'version': '0.2.0',
    'description': 'Vector-Search API of databases.',
    'long_description': None,
    'author': 'AllenChou',
    'author_email': 'f1470891079@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
