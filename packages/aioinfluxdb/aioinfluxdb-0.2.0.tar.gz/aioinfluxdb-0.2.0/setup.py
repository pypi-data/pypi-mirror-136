# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aioinfluxdb']

package_data = \
{'': ['*']}

install_requires = \
['aiocsv>=1.2.1,<2.0.0',
 'aiohttp[speedups]>=3.8.1,<4.0.0',
 'ciso8601>=2.2.0,<3.0.0',
 'isal>=0.11.1,<0.12.0',
 'orjson>=3.6.6,<4.0.0',
 'typing-extensions>=4.0.1,<5.0.0']

extras_require = \
{'pandas:python_version >= "3.8" and python_version < "4.0"': ['pandas>=1.4.0,<2.0.0']}

setup_kwargs = {
    'name': 'aioinfluxdb',
    'version': '0.2.0',
    'description': 'InfluxDB v2 Python SDK with asyncio support',
    'long_description': '# aioinfluxdb\n\n[![PyPI](https://img.shields.io/pypi/v/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)\n[![PyPI - Wheel](https://img.shields.io/pypi/wheel/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)\n[![PyPI - Status](https://img.shields.io/pypi/status/aioinfluxdb?style=flat-square)](https://pypi.org/project/aioinfluxdb/)\n![Codecov](https://img.shields.io/codecov/c/gh/isac322/aioinfluxdb?style=flat-square&logo=codecov)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/isac322/aioinfluxdb/CI?style=flat-square&logo=github)\n![License](https://img.shields.io/github/license/isac322/aioinfluxdb?style=flat-square&logo=github)\n![GitHub last commit](https://img.shields.io/github/last-commit/isac322/aioinfluxdb?logo=github&style=flat-square)\n![Dependabpt Status](https://flat.badgen.net/github/dependabot/isac322/aioinfluxdb?icon=github)\n\nThe Python client for InfluxDB v2 supports asyncio.\n\n**This is early-stage project**\n\n## Why aioinfluxdb?\n\n[The official client](https://pypi.org/project/influxdb-client/) does not supports asyncio that can get significant\nperformance. and [aioinflux](https://pypi.org/project/aioinflux/) does not supports InfluxDB v2.\n\n## Feature table\n\n| Feature               | Sub category                                                 | ✅ / ⚠ / 🚧 |\n|:----------------------|:-------------------------------------------------------------|:----------:|\n| Query                 | Query Data                                                   |     ✅      |\n| Query                 | Analyzer Flux Query                                          |     🚧     |\n| Query                 | Generate AST from Query                                      |     🚧     |\n| Query                 | Retrieve query suggestions                                   |     🚧     |\n| Query                 | Retrieve query suggestions <br /> for a branching suggestion |     🚧     |\n| Write                 |                                                              |     ✅      |\n| Buckets               |                                                              |     ⚠      |\n| Dashboards            |                                                              |     🚧     |\n| Tasks                 |                                                              |     🚧     |\n| Resources             |                                                              |     🚧     |\n| Authorizations        |                                                              |     🚧     |\n| Organizations         |                                                              |     ⚠      |\n| Users                 |                                                              |     🚧     |\n| Health                |                                                              |     🚧     |\n| Ping                  |                                                              |     ✅      |\n| Ready                 |                                                              |     🚧     |\n| Routes                |                                                              |     🚧     |\n| Backup                |                                                              |     🚧     |\n| Cells                 |                                                              |     🚧     |\n| Checks                |                                                              |     🚧     |\n| DBRPs                 |                                                              |     🚧     |\n| Delete                |                                                              |     🚧     |\n| Labels                |                                                              |     🚧     |\n| NotificationEndpoints |                                                              |     🚧     |\n| NotificationRules     |                                                              |     🚧     |\n| Restore               |                                                              |     🚧     |\n| Rules                 |                                                              |     🚧     |\n| Scraper Targets       |                                                              |     🚧     |\n| Secrets               |                                                              |     🚧     |\n| Setup                 |                                                              |     🚧     |\n| Signin                |                                                              |     🚧     |\n| Signout               |                                                              |     🚧     |\n| Sources               |                                                              |     🚧     |\n| Telegraf Plugins      |                                                              |     🚧     |\n| Telegrafs             |                                                              |     🚧     |\n| Templates             |                                                              |     🚧     |\n| Variables             |                                                              |     🚧     |\n| Views                 |                                                              |     🚧     |\n\n---\n\nThis project borrows some de/serialization code from [influxdb-client](https://github.com/influxdata/influxdb-client-python).',
    'author': 'Byeonghoon Yoo',
    'author_email': 'bh322yoo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
