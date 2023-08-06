# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_schema']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'views-schema',
    'version': '2.3.0',
    'description': 'A package containing pydantic models used throughout ViEWS 3 for communication between services',
    'long_description': '\n# ViEWS schema\n\nData models used throughout ViEWS 3 to facilitate communication between services.\n\n```\npip install views-schema\n```\n',
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/prio-data/views_schema',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
