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


from timeit import default_timer as timer

import click

from .cypher import cypher_str


class DataInterchangeFormat(object):

    def write_result(self, result, limit=0):
        raise NotImplementedError()

    def write_record(self, record):
        raise NotImplementedError()

    def write_value(self, value):
        raise NotImplementedError()


class SeparatedValues(DataInterchangeFormat):

    styles = {
        "NoneType": {"fg": "black", "bold": True},
    }

    def __init__(self, headers=1, field_separator="\t", record_separator="\r\n"):
        self.headers = headers
        self.field_separator = field_separator
        self.record_separator = record_separator

    def write_result(self, result, limit=0):
        count = 0
        keys = result.keys()
        if keys:
            for count, record in enumerate(result, start=1):
                if count == 1 and self.headers:
                    click.secho(self.field_separator.join(keys), nl=False, fg="cyan")
                    click.echo(self.record_separator, nl=False)
                self.write_record(record)
                if count == limit:
                    break
        return count

    def write_record(self, record):
        for i, value in enumerate(record.values()):
            if i > 0:
                click.echo(self.field_separator, nl=False)
            self.write_value(value)
        click.echo(self.record_separator, nl=False)

    def write_value(self, value):
        try:
            style = self.styles[type(value).__name__]
        except KeyError:
            style = {"fg": "reset", "bold": False}
        click.secho(cypher_str(value), nl=False, **style)


class TabularValues(DataInterchangeFormat):

    def __init__(self):
        pass

    def write_result(self, result, limit=0):
        keys = result.keys()
        widths = list(map(len, keys))
        data = []
        for record in result:
            fields = []
            for i, value in enumerate(record):
                encoded_value = cypher_str(value)
                widths[i] = max(widths[i], len(encoded_value))
                fields.append(encoded_value)
            data.append(fields)
        # TODO

    def write_record(self, record):
        pass

    def write_value(self, value):
        pass
