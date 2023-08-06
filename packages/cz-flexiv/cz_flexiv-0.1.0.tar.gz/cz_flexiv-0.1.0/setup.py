# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['cz_flexiv']
install_requires = \
['commitizen>=2.27.1,<3.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'cz-flexiv',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'yunpeng.zhan',
    'author_email': 'yunpeng.zhan@flexiv.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
