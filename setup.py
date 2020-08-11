#!/usr/bin/env python

import os

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    name = 'pyreds',
    packages = ['pyreds'],
    version = '0.1.4',
    description = 'Simple full text search module for Python, backed by Redis',
    long_description = long_description,
    author = 'Tan Shuai',
    author_email = '7anshuai@gmail.com',
    url = 'https://github.com/7anshuai/pyreds',
    download_url = 'https://github.com/7anshuai/pyreds/archive/0.1.3.tar.gz',
    keywords = ['redis', 'full text search'],
    license='MIT',
    install_requires = [
        'nltk==3.4.5',
        'redis==2.10.6'
    ],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ]
)
