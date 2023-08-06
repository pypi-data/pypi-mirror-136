'''
Author: Liu Yancheng
Description: test
Date: 2022-01-29 12:15:08
LastEditTime: 2022-01-29 14:49:59
LastEditors: Liu Yancheng
'''

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
    
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'),encoding='utf-8') as fh:
    long_description="\n"+fh.read()

VERSION ="0.0.1"
DESCRIPTION =""
LONG_DESCRIPTION =""

setup(
    name="myImport",
    version=VERSION,
    author="Liu Yancheng",
    author_email="1418381215@qq.com",
    url="https://gitee.com/qq1418381215/myImport",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["numpy"],
    keywords=["value"]
)
