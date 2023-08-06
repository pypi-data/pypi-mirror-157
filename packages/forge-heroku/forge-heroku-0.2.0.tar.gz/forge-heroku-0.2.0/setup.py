# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forgeheroku', 'forgeheroku.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=2.0.0',
 'forge-core<1.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0']

entry_points = \
{'console_scripts': ['forge-heroku = forgeheroku:cli']}

setup_kwargs = {
    'name': 'forge-heroku',
    'version': '0.2.0',
    'description': 'Work library for Forge',
    'long_description': '# forge-heroku\n\nDeploy a Django project to Heroku with minimal configuration.\n\nThis package is specifically designed to work with Forge and the [Forge buildpack](https://github.com/forgepackages/heroku-buildpack-forge).\n\n\n## Installation\n\n### Forge installation\n\nThe `forge-heroku` package is a dependency of [`forge`](https://github.com/forgepackages/forge) and is available as `forge heroku`.\n\nIf you use the [Forge quickstart](https://www.forgepackages.com/docs/quickstart/),\neverything you need will already be set up.\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.forgepackages.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
