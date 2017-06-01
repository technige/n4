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


import sys

import click

from n4.cypher import cypher_repr, cypher_str
from n4.table import Table

if sys.version_info >= (3,):
    BOOLEAN = bool
    INTEGER = int
    FLOAT = float
    BYTES = (bytes, bytearray)
    STRING = str
    LIST = list
    MAP = dict
else:
    BOOLEAN = bool
    INTEGER = (int, long)
    FLOAT = float
    BYTES = bytearray
    STRING = unicode
    LIST = list
    MAP = dict


class DataInterchangeFormat(object):

    def write_result(self, result):
        raise NotImplementedError()


class SeparatedValues(DataInterchangeFormat):

    def __init__(self, field_separator, header=1):
        self.field_separator = field_separator
        self.header = header

    def write_result(self, result):
        count = 0
        if self.header:
            click.secho(self.field_separator.join(result.keys()), nl=False, fg="cyan")
            click.echo(u"\r\n", nl=False)
        for count, record in enumerate(result, start=1):
            self.write_record(record)
        return count

    def write_record(self, record):
        for i, value in enumerate(record.values()):
            if i > 0:
                click.echo(self.field_separator, nl=False)
            self.write_value(value)
        click.echo(u"\r\n", nl=False)

    def write_value(self, value, **style):
        click.secho(cypher_str(value), nl=False, **style)


class CommaSeparatedValues(SeparatedValues):

    def __init__(self, header=1):
        super(CommaSeparatedValues, self).__init__(",", header)

    def write_value(self, value, **style):
        if isinstance(value, STRING):
            if u',' in value or u'"' in value or u"\r" in value or u"\n" in value:
                escaped_value = u'"' + value.replace(u'"', u'""') + u'"'
                click.secho(escaped_value, nl=False, **style)
            else:
                click.secho(cypher_repr(value, quote=u'"'), nl=False, **style)
        else:
            click.secho(cypher_str(value), nl=False, **style)


class TabSeparatedValues(SeparatedValues):

    def __init__(self, header=1):
        super(TabSeparatedValues, self).__init__(u"\t", header)

    def write_value(self, value, **style):
        if isinstance(value, STRING):
            click.secho(cypher_repr(value, quote=u'"'), nl=False, **style)
        else:
            click.secho(cypher_str(value), nl=False, **style)


class DataTable(DataInterchangeFormat):

    def __init__(self, header=1, page_limit=50, page_gap=1):
        self.header = header
        self.page_limit = page_limit
        self.page_gap = page_gap
        self.header_style = {
            "fg": "cyan",
        }

    def write_result(self, result):
        keys = result.keys()
        table = Table(keys)
        for count, record in enumerate(result, start=1):
            table.append(record.values())
            if count == self.page_limit:
                break
        table.echo(header_style=self.header_style)
        click.echo("\r\n" * self.page_gap, nl=False)
        return table.size()
