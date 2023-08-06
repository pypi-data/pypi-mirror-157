# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redis_admin_client']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0',
 'ipcalc>=1.99.0,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pandasql>=0.7.3,<0.8.0',
 'plotly-express>=0.4.1,<0.5.0',
 'plotly>=5.9.0,<6.0.0',
 'ray>=1.13.0,<2.0.0',
 'redis>=4.3.4,<5.0.0',
 'requests>=2.28.1,<3.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'redis-admin-client',
    'version': '0.1.1',
    'description': 'High level redis client',
    'long_description': None,
    'author': 'Kharthigeyan Satyamurthy',
    'author_email': 'kharthigeyan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
