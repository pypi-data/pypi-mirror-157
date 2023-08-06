# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['burny_common']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'loguru>=0.6.0,<0.7.0',
 'paramiko>=2.11.0,<3.0.0',
 'portpicker>=1.5.2,<2.0.0',
 'psutil>=5.9.1,<6.0.0',
 'requests>=2.28.0,<3.0.0',
 'types-requests>=2.27.31,<3.0.0']

setup_kwargs = {
    'name': 'burny-common',
    'version': '0.0.7',
    'description': '',
    'long_description': None,
    'author': 'BurnySc2',
    'author_email': 'gamingburny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
