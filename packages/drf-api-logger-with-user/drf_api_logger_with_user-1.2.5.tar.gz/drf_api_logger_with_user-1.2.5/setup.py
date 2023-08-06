# Copyright (c) 2020-2021 Vishal Anand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

import re

import setuptools


def get_long_desc():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


PACKAGE_NAME = 'drf_api_logger_with_user'
SOURCE_DIRECTORY = 'drf_api_logger_with_user'
SOURCE_PACKAGE_REGEX = re.compile(rf'^{SOURCE_DIRECTORY}')

source_packages = setuptools.find_packages(include=[SOURCE_DIRECTORY, f'{SOURCE_DIRECTORY}.*'])
proj_packages = [SOURCE_PACKAGE_REGEX.sub(PACKAGE_NAME, name) for name in source_packages]

setuptools.setup(
    name="drf_api_logger_with_user",
    version="1.2.5",
    author="Hamid Soltani",
    author_email="pandora10mk@gmail.com",
    description="An API Logger for your Django Rest Framework project.",
    long_description=get_long_desc(),
    long_description_content_type="text/markdown",
    url="https://github.com/HAM1DR37A/DRF-API-Logger/",
    packages=proj_packages,
    package_dir={PACKAGE_NAME: SOURCE_DIRECTORY},
    install_requires=["djangorestframework>=3.7.4", "bleach>=3.1.5"],
    license='MIT',
    python_requires='>=3.6',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Operating System :: OS Independent",
    ],
)
