#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup, find_packages

# Read the version from file
with open(
    path.join(path.dirname(__file__), 'commandio', 'misc', 'version.txt')
) as fid:
    version = fid.read().strip()

# Read the contents of the README file
with open(
    path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
    encoding='utf-8',
) as fid:
    readme = fid.read()

if __name__ == "__main__":
    setup(
        name="commandio",
        version=version,
        packages=find_packages(exclude=['tests']),
        license='GPL-3.0 License',
        classifiers=[
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: System :: Software Distribution",
            "Topic :: Utilities",
        ],
        python_requires='>=3.7',
        setup_requires=["pytest-runner"],
        tests_require=["pytest", "pytest-cov", "coverage"],
        keywords="Command line shell UNIX Windows",
        description="Python package that logs and executes commands for the command line.",
        long_description=readme,
        long_description_content_type='text/x-rst',
        author='Adebayo Braimah',
        author_email='adebayo.braimah@gmail.com',
        include_package_data=True,
        url='https://github.com/AdebayoBraimah/commandio',
    )
