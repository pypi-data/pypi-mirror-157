# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_sio', 'fastapi_sio.schemas']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.73.0,<1.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-socketio>=4.0.0,<6.0.0',
 'websockets>=10.2,<11.0']

setup_kwargs = {
    'name': 'fastapi-sio',
    'version': '0.3.0',
    'description': 'Socket.io for FastAPI with AsyncAPI documentation',
    'long_description': '# fastapi-sio\n\n![FastAPI library](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)\n![Socket.io](https://img.shields.io/badge/-Socket.io-black?logo=socket.io&logoColor=white)\n![Uses AsyncAPI](https://img.shields.io/badge/-AsyncAPI-4f8fbe)\n![Current state](https://img.shields.io/badge/status-in_development-orange)\n\n**Socket.io FastAPI integration library with first-class documentation using AsyncAPI**\n\nThe usage of the library is very familiar to the experience you‘re used to in FastAPI. Automatic documentation, type hints everywhere and heavy use of Pydantic.\n\n## Features\n\n- First-class generated specification & documentation\n- Uses [python_socketio](https://python-socketio.readthedocs.io/en/latest/) underneath\n- Fully typed using pydantic, including the [AsyncAPI spec](./fastapi_sio/schemas/asyncapi.py)\n- Streamlined emit to clients ([learn more in docs](./docs/emitting.md))\n- Forces strictly to emit correct data type  ([see the example](./docs/example.md))\n\n## What‘s Missing?\n  \n- [ ] Serve AsyncAPI studio at /sio/docs\n    - Unfortunately, AsyncAPI studio doesn‘t work the same way as Swagger UI, there is currently no way to use CDN hosted built package and supply only single html file and URL with spec JSON\n- [ ] Support for more obscure fields of AsyncAPI, such as `traits`, ...\n\n## Usage Example\n\n```python\nfastapi_app = FastAPI()\nsio_app = FastAPISIO(app=fastapi_app)\n\npurr_channel = sio_app.create_emitter(\n    "purrs",\n    model=PurrModel,\n    summary="Channel for purrs",\n    description="Receive any purrs here!",\n)\n\n@sio_app.on(\n    "rubs",\n    model=BellyRubModel,\n    summary="Channel for belly rubs",\n    description="Send your belly rubs through here!",\n)\nasync def handle_rub(sid, data):\n    await purr_channel.emit(\n        PurrModel(loudness=2, detail="Purr for all listeners")\n    )\n    return "Ack to the one who rubbed"\n```\n\n👉 [Check out the example AsyncAPI documentation output!](https://studio.asyncapi.com/?url=https://raw.githubusercontent.com/marianhlavac/fastapi-sio/master/examples/from_readme_asyncapi.json)\n\nBy default (you can change these values):\n - the Socket.io endpoint path is **`/sio/socket.io`** (the `socket.io` part is set automatically by some clients)\n - The AsyncAPI spec file is at **`/sio/docs/asyncapi.json`**\n\nFind more in the [examples](/docs/examples.md).\n\n## Documentation & Reference\n\nRefer to the [/docs](./docs/index.md) directory to learn how to use this library in your project.\n\n_TODO: This documentation will be hosted on Github Pages in the near future, hopefully._\n\n\n## Contribution\n\n...\n\n## Used by\n\n<a href="https://dronetag.cz"><img src="https://dronetag.cz/assets/logo-full.svg" height="32" /></a>\n\n[Feel free to open a PR](https://github.com/marianhlavac/fastapi-sio/pulls) to add your project or company to this list.',
    'author': 'Marian Hlavac',
    'author_email': 'm@marianhlavac.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
