#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
readme = open('README.md').read()
doclink="http://waterdoc.readthedocs.io/"

setup(
    name="hydromodel",  # 输入项目名称
    version="0.0.4",  # 输入版本号
    keywords=[""],  # 输入关键词
    description="xin an jiang",  # 输入概述
    long_description=readme+'\n\n'+doclink,  # 输入描述

    url="https://github.com/iHeadWater/Process_HydroXAJ",  # 输入项目Github仓库的链接
    author="Ouyang_Wenyu",  # 输入作者名字
    author_email="",  # 输入作者邮箱
    license="GPLv3",  # 此为声明文件，一般填写 MIT_license

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[""],  # 输入项目所用的包
    python_requires='>=3.7',  # Python版本要求
)
