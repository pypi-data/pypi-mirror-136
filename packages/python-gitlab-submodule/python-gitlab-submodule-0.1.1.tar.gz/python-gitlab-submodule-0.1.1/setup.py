#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('README.md', 'r', encoding='utf-8') as readme:
    long_description = readme.read()

from setuptools import setup

setup(
    name='python-gitlab-submodule',
    description='python-gitlab-submodule: '
                'List project submodules and get the commits they point to '
                'with python-gitlab.',
    license='Apache License 2.0',
    version='0.1.1',
    author='Valentin François',
    maintainer='Valentin François',
    url='https://github.com/ValentinFrancois/python-gitlab-submodule',
    packages=['gitlab_submodule'],
    install_requires=[
       'python-gitlab>=3.0.0',
       'giturlparse>=0.10.0',
    ],
    platforms=['any'],
    python_requires='>=3.7',
    license_files=['LICENSE.txt'],
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    long_description=long_description,
)
