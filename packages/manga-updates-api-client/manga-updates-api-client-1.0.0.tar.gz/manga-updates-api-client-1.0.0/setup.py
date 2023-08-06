# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manga_updates_api_client',
 'manga_updates_api_client.api',
 'manga_updates_api_client.api.aboutus',
 'manga_updates_api_client.api.account',
 'manga_updates_api_client.api.authors',
 'manga_updates_api_client.api.categories',
 'manga_updates_api_client.api.convo',
 'manga_updates_api_client.api.faq',
 'manga_updates_api_client.api.forum',
 'manga_updates_api_client.api.genre',
 'manga_updates_api_client.api.groups',
 'manga_updates_api_client.api.lists',
 'manga_updates_api_client.api.members',
 'manga_updates_api_client.api.misc',
 'manga_updates_api_client.api.poll',
 'manga_updates_api_client.api.publishers',
 'manga_updates_api_client.api.releases',
 'manga_updates_api_client.api.reviews',
 'manga_updates_api_client.api.series',
 'manga_updates_api_client.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.3.0', 'httpx>=0.15.4,<0.24.0', 'python-dateutil>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'manga-updates-api-client',
    'version': '1.0.0',
    'description': 'A client library for accessing MangaUpdates API',
    'long_description': '# manga-updates-api-client\nA client library for accessing MangaUpdates API\n\n## Usage\nFirst, create a client:\n\n```python\nfrom manga_updates_api_client import Client\n\nclient = Client(base_url="https://api.mangaupdates.com/v1")\n```\n\nIf the endpoints you\'re going to hit require authentication, use `AuthenticatedClient` instead:\n\n```python\nfrom manga_updates_api_client import AuthenticatedClient\n\nclient = AuthenticatedClient(base_url="https://api.mangaupdates.com/v1", token="SuperSecretToken")\n```\n\nNow call your endpoint and use your models:\n\n```python\nfrom manga_updates_api_client.models import MyDataModel\nfrom manga_updates_api_client.api.my_tag import get_my_data_model\nfrom manga_updates_api_client.types import Response\n\nmy_data: MyDataModel = get_my_data_model.sync(client=client)\n# or if you need more info (e.g. status_code)\nresponse: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)\n```\n\nOr do the same thing with an async version:\n\n```python\nfrom manga_updates_api_client.models import MyDataModel\nfrom manga_updates_api_client.api.my_tag import get_my_data_model\nfrom manga_updates_api_client.types import Response\n\nmy_data: MyDataModel = await get_my_data_model.asyncio(client=client)\nresponse: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)\n```\n\nBy default, when you\'re calling an HTTPS API it will attempt to verify that SSL is working correctly. Using certificate verification is highly recommended most of the time, but sometimes you may need to authenticate to a server (especially an internal server) using a custom certificate bundle.\n\n```python\nclient = AuthenticatedClient(\n    base_url="https://api.mangaupdates.com/v1", \n    token="SuperSecretToken",\n    verify_ssl="/path/to/certificate_bundle.pem",\n)\n```\n\nYou can also disable certificate validation altogether, but beware that **this is a security risk**.\n\n```python\nclient = AuthenticatedClient(\n    base_url="https://api.mangaupdates.com/v1", \n    token="SuperSecretToken", \n    verify_ssl=False\n)\n```\n\nThings to know:\n1. Every path/method combo becomes a Python module with four functions:\n    1. `sync`: Blocking request that returns parsed data (if successful) or `None`\n    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.\n    1. `asyncio`: Like `sync` but async instead of blocking\n    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking\n\n1. All path/query params, and bodies become method arguments.\n1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)\n1. Any endpoint which did not have a tag will be in `manga_updates_api_client.api.default`\n\n## Building / publishing this Client\nThis project uses [Poetry](https://python-poetry.org/) to manage dependencies  and packaging.  Here are the basics:\n1. Update the metadata in pyproject.toml (e.g. authors, version)\n1. If you\'re using a private repository, configure it with Poetry\n    1. `poetry config repositories.<your-repository-name> <url-to-your-repository>`\n    1. `poetry config http-basic.<your-repository-name> <username> <password>`\n1. Publish the client with `poetry publish --build -r <your-repository-name>` or, if for public PyPI, just `poetry publish --build`\n\nIf you want to install this client into another project without publishing it (e.g. for development) then:\n1. If that project **is using Poetry**, you can simply do `poetry add <path-to-this-client>` from that project\n1. If that project is not using Poetry:\n    1. Build a wheel with `poetry build -f wheel`\n    1. Install that wheel from the other project `pip install <path-to-wheel>`\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
