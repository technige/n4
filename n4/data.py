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

from n4.cypher import cypher_repr, cypher_str


try:
    unicode
except NameError:
    string = str
    unicode = str
else:
    string = (str, unicode)
    unicode = unicode


class DataInterchangeFormat(object):

    def write_result(self, result):
        raise NotImplementedError()

    def write_record(self, record):
        raise NotImplementedError()

    def write_value(self, value, **style):
        raise NotImplementedError()


class SeparatedValues(DataInterchangeFormat):

    def __init__(self, field_separator, record_separator="\r\n", header=1):
        self.field_separator = field_separator
        self.record_separator = record_separator
        self.header = header

    def write_result(self, result):
        count = 0
        if self.header:
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

    def write_value(self, value, **style):
        click.secho(cypher_str(value), nl=False, **style)


class CommaSeparatedValues(SeparatedValues):

    def __init__(self, header=1, record_separator="\r\n"):
        super(CommaSeparatedValues, self).__init__(",", record_separator, header)

    def write_value(self, value, **style):
        if isinstance(value, string):
            if ',' in value or '"' in value or "\r" in value or "\n" in value:
                escaped_value = '"' + value.replace('"', '""') + '"'
                click.secho(escaped_value, nl=False, **style)
            else:
                click.secho(cypher_repr(value, quote='"'), nl=False, **style)
        else:
            click.secho(cypher_str(value), nl=False, **style)


class TabSeparatedValues(SeparatedValues):

    def __init__(self, header=1, record_separator="\r\n"):
        super(TabSeparatedValues, self).__init__("\t", record_separator, header)

    def write_value(self, value, **style):
        if isinstance(value, string):
            click.secho(cypher_repr(value, quote='"'), nl=False, **style)
        else:
            click.secho(cypher_str(value), nl=False, **style)


class DataTable(DataInterchangeFormat):

    def __init__(self, header=1, page_limit=50, page_gap=1):
        self.header = header
        self.page_limit = page_limit
        self.page_gap = page_gap
        self.metadata_style = {
            "fg": "cyan",
        }

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
            if count == self.page_limit:
                break

        if self.header:
            click.secho(" " + " | ".join(key.ljust(widths[i]) for i, key in enumerate(keys)) + " ",
                        nl=False, **self.metadata_style)
            click.echo("\r\n", nl=False)
            click.secho("|".join("-" * (widths[i] + 2) for i, key in enumerate(keys)),
                        nl=False, **self.metadata_style)
            click.echo("\r\n", nl=False)
        for y, values in enumerate(data):
            self.write_record(data_aligns[y][x](value, widths[x]) for x, value in enumerate(values))

        click.echo("\r\n" * self.page_gap, nl=False)

        return len(data)

    def write_record(self, record):
        for i, value in enumerate(record):
            if i > 0:
                click.secho("|", nl=False, **self.metadata_style)
            self.write_value(value)
        click.echo("\r\n", nl=False)

    def write_value(self, value, **style):
        click.secho(" {} ".format(value), nl=False, **style)

    @classmethod
    def encode_value(cls, value):
        if value is None:
            return u"", unicode.ljust
        elif isinstance(value, bool):
            return cypher_str(value), unicode.ljust
        elif isinstance(value, (int, float)):
            return cypher_str(value), unicode.rjust
        else:
            return cypher_str(value), unicode.ljust
