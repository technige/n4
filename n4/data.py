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


import click

from n4.cypher import cypher_str


class DataInterchangeFormat(object):

    def write_result(self, result):
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

    def write_result(self, result):
        count = 0
        if self.headers:
            click.secho(self.field_separator.join(result.keys()), nl=False, fg="cyan")
            click.echo(self.record_separator, nl=False)
        for count, record in enumerate(result, start=1):
            self.write_record(record)
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

    def __init__(self, headers=1, limit=50):
        self.headers = headers
        self.limit = limit

    def write_result(self, result):
        keys = result.keys()
        widths = list(map(len, keys))
        data = []
        data_aligns = []
        for count, record in enumerate(result, start=1):
            fields = []
            field_aligns = []
            for i, value in enumerate(record.values()):
                encoded_value, align = self.encode_value(value)
                widths[i] = max(widths[i], len(encoded_value))
                fields.append(encoded_value)
                field_aligns.append(align)
            data.append(fields)
            data_aligns.append(field_aligns)
            if count == self.limit:
                break

        if self.headers:
            click.echo(" ", nl=False)
            click.secho(" | ".join(key.ljust(widths[i]) for i, key in enumerate(keys)), nl=False, fg="cyan")
            click.echo(" \r\n", nl=False)
            click.secho("-".join("-" * (widths[i] + 2) for i, key in enumerate(keys)), nl=False, fg="cyan")
            click.echo("\r\n", nl=False)
        for y, values in enumerate(data):
            self.write_record(data_aligns[y][x](value, widths[x]) for x, value in enumerate(values))

        return len(data)

    def write_record(self, record):
        click.echo(" ", nl=False)
        for i, value in enumerate(record):
            if i > 0:
                click.echo(" | ", nl=False)
            self.write_value(value)
        click.echo(" \r\n", nl=False)

    def write_value(self, value):
        click.echo(value, nl=False)

    @classmethod
    def encode_value(cls, value):
        if value is None:
            return "", str.ljust
        elif isinstance(value, (int, float)):
            return cypher_str(value), str.rjust
        else:
            return cypher_str(value), str.ljust
