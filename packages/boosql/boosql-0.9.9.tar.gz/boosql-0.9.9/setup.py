# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['boosql', 'boosql.exceptions']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'boosql',
    'version': '0.9.9',
    'description': '',
    'long_description': None,
    'author': 'yer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
