#!/usr/bin/env python

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import sys
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="awscli-plugin-tls",
    packages=["awscli_plugin_tls"],
    version="0.1",
    description="TLS configuration plugin for AWS CLI",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Ryan Festag",
    author_email="ryfestag@amazon.com",
    url="https://github.com/awslabs/awscli-plugin-tls",
    download_url="https://github.com/awslabs/awscli-plugin-tls/awscli-plugin-tls-v0.1.tgz",
    keywords=["awscli", "plugin", "tls"],
    license="Apache License 2.0",
    install_requires=["botocore"],
    classifiers=[],
)
