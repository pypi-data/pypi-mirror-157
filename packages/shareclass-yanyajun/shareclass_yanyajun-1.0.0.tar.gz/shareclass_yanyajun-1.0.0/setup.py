# -*- coding: utf-8 -*-
# @Time    : 2022/7/1 下午10:46
# @Author  : yanyajun

with open("README.md", "r") as fh:
  long_description = fh.read()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import setuptools


setup(
    name='shareclass_yanyajun',  # 包的名字
    version='1.0.0',  # 版本号
    author="yanyajun",
    author_email="yyjjbz@163.com",
    description='测试项目 看一下行不行',
    long_description=long_description,
    packages=setuptools.find_packages(),  # 包需要引用的文件夹
    include_package_data=True,

    # 依赖包, 应用到的第三方库
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ]
)