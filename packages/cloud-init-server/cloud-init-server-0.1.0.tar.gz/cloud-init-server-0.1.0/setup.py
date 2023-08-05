# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloud_init_server']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'fastapi>=0.78.0,<0.79.0',
 'fs>=2.4.16,<3.0.0',
 'prometheus-fastapi-instrumentator>=5.8.2,<6.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'slowapi>=0.1.5,<0.2.0',
 'uvicorn>=0.18.1,<0.19.0']

setup_kwargs = {
    'name': 'cloud-init-server',
    'version': '0.1.0',
    'description': 'Simple HTTP serving cloud-init metadata files',
    'long_description': None,
    'author': 'Piotr Styczyński',
    'author_email': 'piotr@styczynski.in',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
