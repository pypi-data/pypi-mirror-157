#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools
from textwrap import dedent

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "2.0.0"

setuptools.setup(
    name='atom_access',
    version=__version__,
    author='Chilton Group',
    author_email='nicholas.chilton@manchester.ac.uk',
    description=dedent(
        'atom_access is a ray tracing package for addressing the steric \
         hinderance of molecules'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/chilton-group/atom_access",
    project_urls={
        "Bug Tracker": "https://gitlab.com/chilton-group/atom_access/-/issues",
        "Documentation": "https://chilton-group.gitlab.io/atom_access/"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
        ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'xyz_py>=4.5.0',
        'plotly',
        'scikit-learn'
        ],
    entry_points={
        'console_scripts': [
            'atom_access = atom_access.cli:main'
            ]
        }
    )
