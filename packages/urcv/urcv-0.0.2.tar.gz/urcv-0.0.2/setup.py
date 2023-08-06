#!/usr/bin/env python

import os
from pathlib import Path
import pkg_resources
from setuptools import setup, find_namespace_packages

os.environ['PYTHON_EGG_CACHE'] = '.eggs'

with Path("urcv/__version__").open() as f:
    version = f.read()

with Path("requirements.txt").open() as f:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(f)
    ]

setup(
    name="urcv",
    version=version,
    packages=find_namespace_packages(),
    install_requires=install_requires,
    description="",
    author="",
    author_email="",
    url="https://github.com/chriscauley/urcv",
)
