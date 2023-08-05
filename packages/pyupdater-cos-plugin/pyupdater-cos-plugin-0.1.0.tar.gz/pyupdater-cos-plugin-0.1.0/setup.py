# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uploader']

package_data = \
{'': ['*']}

install_requires = \
['cos-python-sdk-v5>=1.9.20,<2.0.0']

setup_kwargs = {
    'name': 'pyupdater-cos-plugin',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': '杨志勇',
    'author_email': 'eye.zhi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
