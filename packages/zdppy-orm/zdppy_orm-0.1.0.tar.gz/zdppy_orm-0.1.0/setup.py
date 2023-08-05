# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdppy_orm']

package_data = \
{'': ['*']}

install_requires = \
['zdppy-mysql>=0.2.5,<0.3.0']

setup_kwargs = {
    'name': 'zdppy-orm',
    'version': '0.1.0',
    'description': 'Python ORM框架，完美兼容zdppy_api',
    'long_description': '# zdpppy_orm\n\n基于peewee二次开发\n\n## 版本历史\n\n- v0.1.0 2022/06/29 新增：基本功能',
    'author': 'zhangdapeng520',
    'author_email': 'pygosuperman@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tiangolo/sqlmodel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
