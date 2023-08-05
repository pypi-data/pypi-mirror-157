# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['s3_cli']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.18,<2.0.0']

setup_kwargs = {
    'name': 's3-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Diogo Neto',
    'author_email': 'diogo.neto@promptlyhealth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
