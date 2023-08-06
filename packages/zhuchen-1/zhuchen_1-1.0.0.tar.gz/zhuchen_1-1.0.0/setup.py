# -*- coding: utf-8 -*-
# @File : setup.py
# @Author : 朱臣
# @iphone : 15850225717 
# @time : 2022/6/30 12:47

from distutils.core import setup
from setuptools import find_packages

with open("README.rst","r") as f:
    long_description = f.read()

setup(name="zhuchen_1",  # 包名
      version='1.0.0',  # 版本号
      description="A small example package",
      long_description=long_description,
      author="zhuchen",
      author_email='1099560198@qq.com',
      # url='',
      install_requires=[],
      license='BSD License',
      packages=find_packages(),
      platforms=['all'],  # 平台
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )