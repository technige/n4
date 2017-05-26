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


from os import getenv

from .console import Console


def main():
    scheme = "bolt"
    host = "localhost"
    port = 7687
    uri = getenv("NEO4J_URI", "%s://%s:%d" % (scheme, host, port))
    user = getenv("NEO4J_USER", "neo4j")
    password = getenv("NEO4J_PASSWORD", "password")
    auth = (user, password)
    console = Console(uri, auth=auth)
    exit(console.loop())


if __name__ == "__main__":
    main()
