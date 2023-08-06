# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['actor', 'actor.handler', 'actor.response']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'aiofiles>=0.8.0,<0.9.0', 'uvicorn>=0.17.6,<0.18.0']

setup_kwargs = {
    'name': 'uvicorn-actor',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'timoniq',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
