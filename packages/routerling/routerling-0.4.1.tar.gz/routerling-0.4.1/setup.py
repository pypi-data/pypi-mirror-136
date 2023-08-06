# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['routerling']

package_data = \
{'': ['*']}

install_requires = \
['uvicorn>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'routerling',
    'version': '0.4.1',
    'description': 'Extremely Stupid Simple, Blazing Fast, Get Out of your way immediately Microframework for building Python Web Applications.',
    'long_description': '# Routerling\n\n<img src="https://img.shields.io/badge/coverage-92%25-green" />\n\nBuild web applications and enterprise microservices with the _**simplest**_ and possibly the fastest or one of the _**fastest**_ web microframeworks for python.\n\n[Go To Docs](https://rayattack.github.io/routerling)\n',
    'author': 'Raymond Ortserga',
    'author_email': 'ortserga@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
