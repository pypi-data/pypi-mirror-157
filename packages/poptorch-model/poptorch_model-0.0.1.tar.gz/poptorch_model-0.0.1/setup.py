#!/usr/bin/env python
#-*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "poptorch_model",      #这里是pip项目发布的名称
    version = "0.0.1",  #版本号，数值大的会优先被pip
    keywords = ("pip", "SICA","featureextraction"),
    description = "poptorch pipeline model base class",
    long_description = "as a replacement for torch.nn.Module for adding pipeline annotations",
    license = "MIT Licence",

    author = "Jinle Tong",
    author_email = "lancertong@live.com",

    packages = find_packages(),
    platforms = "any",
    install_requires = ["torch", "poptorch"]          #这个项目需要的第三方库
)