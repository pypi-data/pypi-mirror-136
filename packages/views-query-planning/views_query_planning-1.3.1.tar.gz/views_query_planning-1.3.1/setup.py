# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_query_planning']

package_data = \
{'': ['*']}

install_requires = \
['PyMonad>=2.4.0,<3.0.0',
 'SQLAlchemy>=1.4.27,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'networkx>=2.6.3,<3.0.0',
 'psycopg2>=2.9.2,<3.0.0',
 'pydot>=1.4.2,<2.0.0',
 'toolz>=0.11.2,<0.12.0']

entry_points = \
{'console_scripts': ['vqp = views_query_planning.cli:vqp']}

setup_kwargs = {
    'name': 'views-query-planning',
    'version': '1.3.1',
    'description': 'Generate queries for relational databases',
    'long_description': '\n# Views Query Planning\n\nThis package exposes a class `views_query_planning.QueryComposer` that makes it\npossible to generate queries against a relational database using a network\nrepresentation of the database. Such networks can be inferred using the\n`views_query_planning.join_network` function that takes a dictionary of\n`sqlalchemy` tables and returns a `networkx.DiGraph` that can be passed to the\ncomposer.\n\nFor an example service that uses the QueryComposer class to expose columns in a\nrelational DB RESTfully, see\n[base_data_retriever](https://github.com/prio-data/base_data_retriever).\n',
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/prio-data/views_query_planning',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
