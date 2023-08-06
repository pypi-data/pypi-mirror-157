# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '..'}

packages = \
['littlepaimon_utils']

package_data = \
{'': ['*'], 'littlepaimon_utils': ['dist/*']}

install_requires = \
['httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'littlepaimon-utils',
    'version': '1.0.0',
    'description': '小派蒙的一些封装好的工具方法',
    'long_description': None,
    'author': '惜月',
    'author_email': '277073121@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
