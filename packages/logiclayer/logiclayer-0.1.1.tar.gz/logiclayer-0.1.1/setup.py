# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logiclayer']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.0,<4.0.0', 'fastapi>=0.75,<1.0']

setup_kwargs = {
    'name': 'logiclayer',
    'version': '0.1.1',
    'description': 'A simple framework to quickly compose and use multiple functionalities as endpoints.',
    'long_description': 'A simple framework to quickly compose and use multiple functionalities as endpoints.  \nLogicLayer is built upon FastAPI to provide a simple way to group functionalities into reusable modules.\n\n<p>\n<a href="https://github.com/Datawheel/logiclayer/releases"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/"><img src="https://flat.badgen.net/github/checks/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>\n</p>\n\n## Getting started\n\nTo generate a new instance of LogicLayer, create a python file and execute this snippet:\n\n```python\n# example.py\n\nimport requests\nfrom logiclayer import LogicLayer\nfrom logiclayer.echo import EchoModule # Example module\n\necho = EchoModule()\n\ndef is_online() -> bool:\n    res = requests.get("http://clients3.google.com/generate_204")\n    return (res.status_code == 204) and (res.headers.get("Content-Length") == "0")\n\nlayer = LogicLayer()\nlayer.add_check(is_online)\nlayer.add_module(echo, prefix="/echo")\n```\n\nThe `layer` object is an ASGI-compatible application, that can be used with uvicorn/gunicorn to run a server, the same way as you would with a FastAPI instance.\n\n```bash\n$ pip install uvicorn[standard]\n$ uvicorn example:layer\n```\n\nNote the `example:layer` is the reference to the `layer` variable in the `example` module, which [points to the ASGI app instance](https://www.uvicorn.org/#usage).\n\n---\n&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  \nThis project is licensed under [MIT](./LICENSE).\n',
    'author': 'Francisco Abarzua',
    'author_email': 'francisco@datawheel.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Datawheel/logiclayer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
