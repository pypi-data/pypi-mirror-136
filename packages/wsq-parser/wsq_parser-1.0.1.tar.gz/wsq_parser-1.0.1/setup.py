#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: Wenzzy
:copyright: (c) 2022 Wenzzy
"""

version = '1.0.1'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wsq_parser',
    version=version,

    author='Wenzzy',

    description=(
        u'Python module for scraping web-sites'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/WenzzyX/wsq_parser.git',
    download_url='https://github.com/WenzzyX/wsq_parser/archive/master.zip',

    packages=['wsq_parser'],
    install_requires=['beautifulsoup4', 'fake-useragent', 'requests', 'lxml'],

    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)