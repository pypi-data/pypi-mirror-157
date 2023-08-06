# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['azql']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'azql',
    'version': '0.0.1',
    'description': 'Azure SQL Suite',
    'long_description': '# AZQL\n\nThis is the start of greate journey, or so... :)\n',
    'author': 'Markus Feiks',
    'author_email': 'github@feyx.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
