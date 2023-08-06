# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['qlient', 'qlient.core', 'qlient.core.schema']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.11.4,<5.0.0', 'platformdirs>=2.5.2,<3.0.0']

setup_kwargs = {
    'name': 'qlient-core',
    'version': '0.1.0b0',
    'description': 'The core for a blazingly fast and modern graphql client designed with simplicity in mind.',
    'long_description': '# Qlient Core: Python GraphQL Client Core Library\n\nThis is the core for a blazingly fast and modern graphql client that was designed with simplicity in mind.',
    'author': 'Daniel Seifert',
    'author_email': 'info@danielseifert.ch',
    'maintainer': 'Daniel Seifert',
    'maintainer_email': 'info@danielseifert.ch',
    'url': 'https://qlient-org.github.io/python-qlient/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
