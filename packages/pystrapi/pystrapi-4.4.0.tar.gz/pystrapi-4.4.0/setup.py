# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pystrapi', 'pystrapi.help']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp', 'requests>=2.25.0,<3.0.0']

setup_kwargs = {
    'name': 'pystrapi',
    'version': '4.4.0',
    'description': 'Work with Strapi from Python via REST API',
    'long_description': "# PyStrapi\n![CI](https://github.com/NoamNol/py-strapi/workflows/CI/badge.svg?event=push)\n![Build and release](https://github.com/NoamNol/py-strapi/workflows/%F0%9F%9A%80%20Build%20and%20release/badge.svg?event=push)\n[![PyPI version](https://badge.fury.io/py/pystrapi.svg)](https://pypi.org/project/pystrapi)\n![pyversions](https://img.shields.io/pypi/pyversions/pystrapi)\n\nWork with [Strapi](https://strapi.io/) from Python via REST API\n\n## Install\n\n```bash\npip install pystrapi\n```\n\n## Examples\n\nQuick start:\n\n```python\nimport asyncio\nfrom pystrapi import StrapiClient\n\nasync def main():\n    strapi = StrapiClient(api_url=strapi_url)\n    await strapi.authorize(your_identifier, your_password) # optional\n    users = await strapi.get_entries('users', filters={'username': {'$eq': 'Pavel'}})\n    user_id = users['data'][0]['id']\n    await strapi.update_entry('users', user_id, data={'username': 'Mark'})\n\nasyncio.run(main())\n```\n\n## Development\n### Install environment:\n```\npython -m venv .env\nsource .env/bin/activate\npoetry install\n```\n\n### Lint\nRun [prospector](https://prospector.landscape.io/):\n```\nprospector\n```\n\n### Unit tests\n```\npytest test/unittests\n```\n\n### Integration tests\nRun Strapi test server (see [instructions](testserver/README.md)), and run integration tests:\n```\npytest test/integration\n```\n\n### Create new release\n\nPush changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).\n\n",
    'author': 'Noam Nol',
    'author_email': 'noamnol19@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NoamNol/py-strapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
