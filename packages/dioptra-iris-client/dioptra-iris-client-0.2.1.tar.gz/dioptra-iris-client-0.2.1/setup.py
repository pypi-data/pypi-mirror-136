# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['iris_client']
install_requires = \
['Authlib>=0.15.5,<0.16.0', 'httpx>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'dioptra-iris-client',
    'version': '0.2.1',
    'description': 'Python client for the Iris API.',
    'long_description': '# 🕸️ Iris Python Client\n\n[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/iris-client/Tests?logo=github)](https://github.com/dioptra-io/iris-client/actions/workflows/tests.yml)\n[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/iris-client?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/iris-client)\n[![PyPI](https://img.shields.io/pypi/v/dioptra-iris-client?logo=pypi&logoColor=white)](https://pypi.org/project/dioptra-iris-client/)\n\nMinimal Python client for the [Iris](https://github.com/dioptra-io/iris) API,\nbuilt on top of [Authlib](https://github.com/lepture/authlib) and [httpx](https://github.com/encode/httpx).\n\n## Installation\n\n```bash\npip install dioptra-iris-client\n```\n\n## Usage\n\n```python\nfrom iris_client import IrisClient, AsyncIrisClient\n\n# NOTE: If the username and/or the password are not specified,\n# they will be retrieved from the `IRIS_USERNAME` and `IRIS_PASSWORD` environment variables.\n\n# Synchronous client\nwith IrisClient("user@example.org", "password") as client:\n    measurements = client.get("/measurements/").json()\n\n# Asynchronous client\nasync with AsyncIrisClient("user@example.org", "password") as client:\n    measurements = (await client.get("/measurements/")).json()\n\n# Helper function to fetch all the results from a paginated endpoint,\n# available for both clients:\nall_measurements = client.all("/measurements/")\n```\n',
    'author': 'Maxime Mouchet',
    'author_email': 'maxime.mouchet@lip6.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dioptra-io/iris-client',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
