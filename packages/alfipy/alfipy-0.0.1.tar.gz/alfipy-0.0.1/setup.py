# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import io
import os

from setuptools import setup, find_packages

dir_path = os.path.abspath(os.path.dirname(__file__))
readme = io.open(os.path.join(dir_path, "README.md"), encoding="utf-8").read()

setup(
    name="alfipy",
    version="0.0.1",
    author="Gremlin, Inc,",
    author_email="sales@gremlin.com",
    url="https://github.com/gremlin/alfipy/",
    packages=find_packages(exclude=["temp*.py", "test"]),
    include_package_data=True,
    license_files = ('LICENSE.txt',),
    description="Application Level Fault Injection: Python Edition",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["asn1crypto", "protobuf", "pycryptodome"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: Other/Proprietary License",
    ],
)
