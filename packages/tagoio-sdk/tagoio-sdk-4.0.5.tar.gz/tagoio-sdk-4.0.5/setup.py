# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tagoio_sdk',
 'tagoio_sdk.common',
 'tagoio_sdk.infrastructure',
 'tagoio_sdk.modules.Account',
 'tagoio_sdk.modules.Analysis',
 'tagoio_sdk.modules.Device',
 'tagoio_sdk.modules.Services',
 'tagoio_sdk.modules.Utils']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'python-socketio[asyncio_client]>=5.6.0,<6.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'tagoio-sdk',
    'version': '4.0.5',
    'description': 'Official Python SDK for TagoIO',
    'long_description': '<br/>\n<p align="center">\n  <img src="https://assets.tago.io/tagoio/sdk.png" width="250px" alt="TagoIO"></img>\n</p>\n\n> NOTE: *This version (4.x.x) is still in development. You can access the current (3.x.x) version in [tago-io/tago-sdk-python](https://github.com/tago-io/tago-sdk-python).*\n\n# TagoIO - Python SDK\n\nOfficial Python SDK for TagoIO\n\n## Installation\n\n```bash\npip install tagoio-sdk\n```\n\n## Quick Example\n\nIf you have any questions, feel free to check our [Help Center](https://help.tago.io/portal/en/home)\n\n### Insert Device Data\n\n```python\nfrom tagoio_sdk import Device\n\nmyDevice = Device({ "token": "my_device_token" })\nresult = myDevice.sendData({\n    "variable": "temperature",\n    "unit": "F",\n    "value": 55,\n    "time": "2015-11-03 13:44:33",\n    "location": { "lat": 42.2974279, "lng": -85.628292 },\n})\n```\n\n### Edit Device Data\n\n```python\nfrom tagoio_sdk import Device\n\nmyDevice = Device({"token": "my_device_token"})\nresult = myDevice.editData(\n    {\n        "id": "id_of_the_data_item",\n        "value": "123",\n        "time": "2022-04-01 12:34:56",\n        "location": {"lat": 42.2974279, "lng": -85.628292},\n    }\n)\n```\n\n## Development Commands\n\n```bash\npoetry install\npoetry run pytest tests/\npoetry run flake8 src\n```\n\n## License\n\nTagoIO SDK for Python is released under the [Apache-2.0 License](https://github.com/tago-io/sdk-python/blob/master/LICENSE)\n',
    'author': 'Tago LLC',
    'author_email': 'contact@tago.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tago.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
