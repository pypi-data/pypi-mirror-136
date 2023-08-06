# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiohttp_validator']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.0,<4.0.0', 'pydantic>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'aiohttp-validator',
    'version': '0.1.1',
    'description': 'aiohttp simple pydantic validator',
    'long_description': "# aiohttp-validator\n\n[![Downloads][download-badge]][download-url]\n[![License][licence-badge]][licence-url]\n[![Python Versions][python-version-badge]][python-version-url]\n\n[download-badge]: https://static.pepy.tech/personalized-badge/aiohttp-validator?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/month\n[download-url]: https://pepy.tech/project/aiohttp-validator\n[licence-badge]: https://img.shields.io/badge/license-Unlicense-blue.svg\n[licence-url]: https://github.com/dapper91/aiohttp-validator/blob/master/LICENSE\n[python-version-badge]: https://img.shields.io/pypi/pyversions/aiohttp-validator.svg\n[python-version-url]: https://pypi.org/project/aiohttp-validator\n\n\naiohttp simple pydantic http request validator\n\n\n## Installation\n\n```shell\npip install aiohttp-validator\n```\n\n\n## A Simple Example\n\n```py\nfrom typing import Any, Dict, List\n\nimport pydantic\nfrom aiohttp import web\n\nimport aiohttp_validator as validator\n\nroutes = web.RouteTableDef()\n\n\nclass RequestHeaders(pydantic.BaseModel):\n    requestId: str\n    timestamp: float = 0.0\n\n\n@routes.get('/')\n@validator.validated()\nasync def simple_get(request: web.Request, headers: RequestHeaders, offset: int = 0):\n    assert isinstance(headers, RequestHeaders)\n    assert isinstance(offset, int)\n\n    return web.Response()\n\n\n@routes.post('/{path}')\n@validator.validated()\nasync def simple_post(request: web.Request, body: Dict[str, Any], path: str, offset: int, limit: int = 10):\n    assert isinstance(body, dict)\n    assert isinstance(path, str)\n    assert isinstance(offset, int)\n    assert isinstance(limit, int)\n\n    return web.Response()\n\n\nclass SubModel(pydantic.BaseModel):\n    l: List[str]\n    i: int\n\n\nclass Body(pydantic.BaseModel):\n    i: int\n    f: float\n    sub: SubModel\n\n\n@routes.post('/{path1}/{path2}')\n@validator.validated()\nasync def pydantic_body(request: web.Request, body: Body, path1: str, path2: int, pages: List[int]):\n    assert isinstance(body, Body)\n    assert isinstance(path1, str)\n    assert isinstance(path2, int)\n    assert isinstance(pages, list)\n\n    return web.Response()\n\n\napp = web.Application()\napp.add_routes(routes)\n\nweb.run_app(app, port=8080)\n\n```",
    'author': 'Dmitry Pershin',
    'author_email': 'dapper1291@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dapper91/aiohttp-validator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
