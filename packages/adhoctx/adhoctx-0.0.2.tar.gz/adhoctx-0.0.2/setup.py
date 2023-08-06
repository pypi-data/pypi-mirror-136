#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
"""

setup(
    name='adhoctx',
    # auto generate version
    use_scm_version=True,
    author='He Bai',
    author_email='bailaohe@gmail.com',

    description='An adhoc context object',

    keywords=["context", "dict"],
    url='https://github.com/bailaohe/adhoctx',
    platforms=["any"],
    classifiers=filter(None, classifiers.split("\n")),

    install_requires=[
        'mergedeep'
    ],

    packages=find_packages('.'),
    package_dir=({'': '.'}),
    zip_safe=False,

    include_package_data=True,
    package_data={'': ['*.json', '*.xml', '*.yml', '*.yaml', '*.tpl']},

    setup_requires=[
        "setuptools_scm>=1.5",
    ],
    # python_requires=">=3.6",
    # download_url='https://github.com/bailaohe/parade/tarball/0.1',
)
