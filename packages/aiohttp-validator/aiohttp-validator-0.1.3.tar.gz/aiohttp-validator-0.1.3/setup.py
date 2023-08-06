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
    'version': '0.1.3',
    'description': 'aiohttp simple pydantic validator',
    'long_description': "# aiohttp-validator\n\n[![Downloads][download-badge]][download-url]\n[![License][licence-badge]][licence-url]\n[![Python Versions][python-version-badge]][python-version-url]\n\n[download-badge]: https://static.pepy.tech/personalized-badge/aiohttp-validator?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/month\n[download-url]: https://pepy.tech/project/aiohttp-validator\n[licence-badge]: https://img.shields.io/badge/license-Unlicense-blue.svg\n[licence-url]: https://github.com/dapper91/aiohttp-validator/blob/master/LICENSE\n[python-version-badge]: https://img.shields.io/pypi/pyversions/aiohttp-validator.svg\n[python-version-url]: https://pypi.org/project/aiohttp-validator\n\n\naiohttp simple pydantic http request validator\n\n\n## Installation\n\n```shell\npip install aiohttp-validator\n```\n\n\n## A Simple Example\n\n```py\nimport datetime as dt\nfrom uuid import UUID\nfrom typing import Any, Dict, List\n\nimport pydantic\nfrom aiohttp import web\n\nimport aiohttp_validator as validator\n\nroutes = web.RouteTableDef()\n\n\n@routes.get('/posts')\n@validator.validated()\nasync def get_posts(request: web.Request, tags: List[str], limit: pydantic.conint(gt=0, le=100), offset: int = 0):\n    assert isinstance(tags, list)\n    assert isinstance(limit, int)\n    assert isinstance(offset, int)\n    # your code here ...\n\n    return web.Response(status=200)\n\n\nclass RequestHeaders(pydantic.BaseModel):\n    requestId: int\n\n\nclass User(pydantic.BaseModel):\n    name: str\n    surname: str\n\n\nclass Post(pydantic.BaseModel):\n    title: str\n    text: str\n    timestamp: float\n    author: User\n    tags: List[str] = pydantic.Field(default_factory=list)\n\n\n@routes.post('/posts/{section}/{date}')\n@validator.validated()\nasync def create_post(request: web.Request, body: Post, headers: RequestHeaders, section: str, date: dt.date):\n    assert isinstance(body, Post)\n    assert isinstance(headers, RequestHeaders)\n    assert isinstance(date, dt.date)\n    assert isinstance(section, str)\n    # your code here ...\n\n    return web.Response(status=201)\n\n\nclass AuthCookies(pydantic.BaseModel):\n    tokenId: UUID\n\n\n@routes.post('/users')\n@validator.validated()\nasync def create_user(request: web.Request, body: Dict[str, Any], headers: RequestHeaders, cookies: AuthCookies):\n    assert isinstance(body, dict)\n    assert isinstance(headers, RequestHeaders)\n    assert isinstance(cookies, AuthCookies)\n    # your code here ...\n\n    return web.Response(status=201)\n\napp = web.Application()\napp.add_routes(routes)\n\nweb.run_app(app, port=8080)\n\n```\n\nIf any path or query parameter name are clashes with body, headers or cookies argument \nfor some reason the last can be renamed:\n\n```py\n@routes.post('/{cookies}')\n@validator.validated(cookies_argname='_cookies')\nasync def method(request: web.Request, body: Dict[str, Any], _cookies: AuthCookies, cookies: str):\n    # your code here ...\n\n    return web.Response(status=201)\n```\n\nIf any argname is `None` the corresponding request part will not be passed to the function\nand argname can be used as a path or query parameter.\n\n```py\n@routes.post('/{body}/{headers}')\n@validator.validated(body_argname=None, headers_argname=None, cookies_argname=None)\nasync def method(request: web.Request, body: str, headers: str, cookies: str = ''):\n    # your code here ...\n\n    return web.Response(status=201)\n```\n",
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
