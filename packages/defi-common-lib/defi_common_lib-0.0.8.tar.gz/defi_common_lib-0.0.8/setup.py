#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from os.path import join

from setuptools import setup

install_requirements = [
    'python-dotenv',
    'dataclasses',
    'pymysql',
    'contracts-lib-py==0.11.0',
    'boto3',
    'botocore',
    'requests',
    'nevermined-sdk-py==0.12.0',
    'nevermined-metadata-driver-filecoin==0.3.0',
    'web3',
    'retry',
    'pytest',
    'pytest-mock',
    'awswrangler'
]

# Required to run setup.py:
setup_requirements = ['pytest-runner']

test_requirements = [
    'pytest',
]

exec(open('defi_common_lib/version.py').read())

packages = ['defi_common_lib']
for d, _, _ in os.walk('defi_common_lib'):
    if os.path.exists(join(d, '__init__.py')):
        packages.append(d.replace(os.path.sep, '.'))


setup(
    author="nevermined-io",
    author_email='root@nevermined.io',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    description="🐳 Nevermined Python SDK.",
    extras_require={
        'test': test_requirements
    },
    install_requires=install_requirements,
    license="Apache Software License 2.0",
    long_description='',
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='defi_common_lib',
    name='defi_common_lib',
    setup_requires=setup_requirements,
    packages=packages,
    test_suite='tests',
    tests_require=test_requirements,
    version=__version__,
    zip_safe=False,
)
