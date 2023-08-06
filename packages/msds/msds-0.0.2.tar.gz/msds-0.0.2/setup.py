#!usr/bin/env python
# -*- coding:utf-8 _*-

"""
@author:    Nundy
@file:      setup.py
@time:      2022/06/28
@desc:      梅赛德斯车主
"""

from setuptools import setup, find_packages

# 常用配置项
VERSION = '0.0.2'
INSTALL_REQUIRES = [
    'pandas',
    'tenacity',
    'inquirer',
    'click',
    'rich'
]

# 配置导出
setup(
    name = 'msds',
    version = VERSION,
    url = 'https://gitee.com/dawajituan',
    description = 'msds tools',
    author = 'Nundy',
    author_email = '18710939328@163.com',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
    install_requires = INSTALL_REQUIRES,
    python_requires = '>=3.10',
    entry_points={
        'console_scripts': [
            'msds = msds.main:main'
        ]
    }
)
