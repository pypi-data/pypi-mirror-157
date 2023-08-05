# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdppy_mysql', 'zdppy_mysql.constants']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'zdppy-mysql',
    'version': '0.2.4',
    'description': '使用python操作MySQL,同步版本,支持事务',
    'long_description': None,
    'author': 'zhangdapeng',
    'author_email': 'pygosuperman@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
