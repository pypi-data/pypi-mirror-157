#!/usr/bin/python3
# -*- coding=utf-8 -*-
# Author: wangxp
"""
功能:
"""
from setuptools import setup, find_packages

setup(
    name='geo_tool',
    version='1.1.2',
    description=(
        '经纬度解析转换工具(Geographic location analysis and conversion tool)'),
    keywords=("detool", "decorators"),
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding='utf-8').read(),
    author='abo123456',
    author_email='abcdef123456chen@sohu.com',
    maintainer='abo123456',
    maintainer_email='abcdef123456chen@sohu.com',
    license='MIT License',
    install_requires=[
        "requests>=2.22.0",
        "geocoder>=1.38.1",
        "googlemaps>=4.4.1",
        "loguru>=0.3.2"
    ],
    packages=find_packages(),
    platforms=["all"],
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ])
