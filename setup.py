#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from n4 import __version__


packages = find_packages(exclude=("test",))
package_metadata = {
    "name": "n4",
    "version": __version__,
    "description": "Cypher console for Neo4j",
    "long_description": "",
    "author": "Nigel Small <technige@nige.tech>",
    "author_email": "n4@nige.tech",
    "url": None,
    "entry_points": {
        "console_scripts": [
            "n4 = n4:main",
        ],
    },
    "packages": packages,
    "py_modules": ["n4"],
    "install_requires": [
        "click",
        "neo4j-driver>=1.3.0",
        "prompt_toolkit",
        "pygments>=2.0",
    ],
    "license": "Apache License, Version 2.0",
    "classifiers": [
        "Development Status :: 3 - Alpha",
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
