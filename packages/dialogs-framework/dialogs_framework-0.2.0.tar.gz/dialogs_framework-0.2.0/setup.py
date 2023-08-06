# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dialogs_framework', 'dialogs_framework.persistence']

package_data = \
{'': ['*']}

install_requires = \
['contextvars>=2.4,<3.0']

setup_kwargs = {
    'name': 'dialogs-framework',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Alon',
    'author_email': 'alon.gal@khealth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
