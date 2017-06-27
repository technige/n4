#!/usr/bin/env python
# coding: utf-8

# Copyright 2011-2017, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from os.path import dirname, join as path_join
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from n4.meta import __version__, description


with open(path_join(dirname(__file__), "README.rst")) as f:
    long_description = f.read()

packages = find_packages(exclude=("test",))
package_metadata = {
    "name": "n4",
    "version": __version__,
    "description": description,
    "long_description": long_description,
    "author": "Nigel Small <technige@nige.tech>",
    "author_email": "n4@nige.tech",
    "url": "http://nige.tech/n4",
    "entry_points": {
        "console_scripts": [
            "n4 = n4.__main__:repl",
            "n4a = n4.auth:main",
        ],
    },
    "packages": packages,
    "py_modules": [],
    "install_requires": [
        "click>=2.0",
        "colorama",
        "neo4j-driver>=1.3.1",
        "prompt_toolkit",
        "pygments>=2.0",
        "technige.cypy==1.0.0b2",
    ],
    "license": "Apache License, Version 2.0",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
        "Topic :: Software Development",
    ],
}

setup(**package_metadata)
