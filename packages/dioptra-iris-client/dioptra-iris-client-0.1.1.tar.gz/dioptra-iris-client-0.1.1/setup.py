# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['iris_client']
install_requires = \
['Authlib>=0.15.5,<0.16.0', 'httpx>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'dioptra-iris-client',
    'version': '0.1.1',
    'description': 'Python client for the Iris API.',
    'long_description': None,
    'author': 'Maxime Mouchet',
    'author_email': 'maxime.mouchet@lip6.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
