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


from time import perf_counter

import click

from .cypher import cypher_str


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
        "Summary": {"fg": "cyan"},
    }

    def __init__(self, headers=1, field_separator="\t", record_separator="\r\n"):
        self.headers = headers
        self.field_separator = field_separator
        self.record_separator = record_separator

    def write_result(self, result):
        last_index = -1
        t0 = perf_counter()
        keys = result.keys()
        if keys:
            if self.headers:
                click.secho(self.field_separator.join(keys), nl=False, fg="cyan")
                click.echo(self.record_separator, nl=False)
            for last_index, record in enumerate(result):
                self.write_record(record)
        count, time = last_index + 1, perf_counter() - t0
        summary = result.summary()
        server_address = "{}:{}".format(*summary.server.address)
        click.secho(u"({} record{} from {} in {:.3f}s)".format(
            count, "" if count == 1 else "s", server_address, time),
            err=True, **self.styles["Summary"])

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
