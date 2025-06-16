#!/usr/bin/env python3
"""
Setup script for Bitbucket CLI.
"""

import os
from setuptools import setup, find_packages

# Get the current directory
current_directory = os.path.abspath(os.path.dirname(__file__))

# Read the README file
with open(os.path.join(current_directory, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements file
requirements_path = os.path.join(current_directory, 'requirements.txt')
if os.path.isfile(requirements_path):
    with open(requirements_path, 'r') as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    install_requires = ['requests>=2.25.0', 'click>=8.0.0', 'tabulate>=0.8.0']

# Get version from GitHub Actions environment variables if available
version = '1.0.0'  # Default version
if 'GITHUB_RUN_NUMBER' in os.environ:
    run_number = os.environ.get('GITHUB_RUN_NUMBER')
    version = f"1.{run_number}.0"

setup(
    name='python-bitbucket-cli',
    version=version,
    author='Md Minhazul Haque',
    author_email='mdminhazulhaque@gmail.com',
    description='A modern command-line interface for Bitbucket repositories',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mdminhazulhaque/python-bitbucket-cli',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'bitbucket-cli=bitbucket.main:app',
            'bb=bitbucket.main:app',  # Short alias
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='bitbucket cli git devops pipeline api',
    python_requires='>=3.7',
    project_urls={
        'Bug Reports': 'https://github.com/mdminhazulhaque/python-bitbucket-cli/issues',
        'Source': 'https://github.com/mdminhazulhaque/python-bitbucket-cli',
    },
)
