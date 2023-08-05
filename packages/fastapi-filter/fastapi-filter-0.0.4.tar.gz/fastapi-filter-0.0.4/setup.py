# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_filter',
 'fastapi_filter.base',
 'fastapi_filter.contrib',
 'fastapi_filter.contrib.mongoengine',
 'fastapi_filter.contrib.sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.78.0,<0.79.0', 'pydantic>=1.9.0,<2.0.0']

extras_require = \
{'all': ['mongoengine>=0.24.1,<0.25.0', 'SQLAlchemy>=1.4.36,<2.0.0'],
 'mongoengine': ['mongoengine>=0.24.1,<0.25.0'],
 'sqlalchemy': ['SQLAlchemy>=1.4.36,<2.0.0']}

setup_kwargs = {
    'name': 'fastapi-filter',
    'version': '0.0.4',
    'description': 'FastAPI filter',
    'long_description': '[![pypi downloads](https://img.shields.io/pypi/dm/fastapi-filter?color=%232E73B2&logo=python&logoColor=%23F9D25F)](https://pypi.org/project/fastapi-filter)\n[![codecov](https://codecov.io/gh/arthurio/fastapi-filter/branch/main/graph/badge.svg?token=I1DVBL1682)](https://codecov.io/gh/arthurio/fastapi-filter)\n[![Netlify Status](https://api.netlify.com/api/v1/badges/83451c4f-76dd-4154-9b2d-61f654eb0704/deploy-status)](https://fastapi-filter.netlify.app/)\n\n# FastAPI filter\n\n## Example\n\n![Swagger UI](https://raw.githubusercontent.com/arthurio/fastapi-filter/main/docs/swagger-ui.png)\n',
    'author': 'Arthur Rio',
    'author_email': 'arthur.rio44@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/arthurio/fastapi-filter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
