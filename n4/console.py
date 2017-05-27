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


from __future__ import division, print_function

import shlex
from os.path import expanduser
from time import perf_counter

from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError

import click

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer

from pygments.lexers.graph import CypherLexer

from .meta import __version__


HELP = """\
N4 is an interactive Cypher environment for use with Neo4j.

Type Cypher at the prompt and press [Enter] to run.

//  to enter multiline mode (press [Esc][Enter] to run)
/?  for help
/x  to exit

Report bugs to n4@nige.tech\
"""
HISTORY_FILE = expanduser("~/.n4_history")
WELCOME = """\
N4 v{} -- Console for Neo4j
Connected to {{}}

//  to enter multiline mode (press [Esc][Enter] to run)
/?  for help
/x  to exit
""".format(__version__)


class ResultFormat(object):

    count = 0
    time = 0.0

    def __init__(self, result):
        self.result = result

    def print_record(self, record):
        raise NotImplementedError()

    def print_result_summary(self):
        summary = self.result.summary()
        server_address = "{}:{}".format(*summary.server.address)
        click.secho(u"({} record{} from {} in {:.3f}s)".format(
            self.count, "" if self.count == 1 else "s", server_address, self.time), fg="cyan", err=True)


class TSV(ResultFormat):

    def print_result(self):
        last_index = -1
        t0 = perf_counter()
        keys = self.result.keys()
        if keys:
            click.secho("\t".join(keys), fg="cyan")
            for last_index, record in enumerate(self.result):
                self.print_record(record)
        self.count, self.time = last_index + 1, perf_counter() - t0
        self.print_result_summary()

    def print_record(self, record):
        click.echo("\t".join(map(str, record.values())))


class Console(object):

    result_format = TSV
    multiline = False

    def __init__(self, uri, auth):
        self.commands = {

            "//": self.set_multiline,
            "/multiline": self.set_multiline,

            "/?": self.help,
            "/h": self.help,
            "/help": self.help,

            "/x": self.exit,
            "/exit": self.exit,

        }
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.history = FileHistory(HISTORY_FILE)
        self.prompt_args = {
            "history": self.history,
            "lexer": PygmentsLexer(CypherLexer),
        }
        print(WELCOME.format(uri))

    def loop(self):
        while True:
            try:
                source = self.read().lstrip()
            except EOFError:
                return 0
            if source.startswith("/"):
                self.execute_command(source)
            elif source:
                try:
                    self.execute_cypher(source)
                except CypherError as error:
                    if error.classification == "ClientError":
                        colour = "yellow"
                    elif error.classification == "DatabaseError":
                        colour = "red"
                    elif error.classification == "TransientError":
                        colour = "magenta"
                    else:
                        colour = "yellow"
                    click.secho("{}: {}".format(error.title, error.message), fg=colour, err=True)
                except ServiceUnavailable:
                    return 1

    def read(self):
        if self.multiline:
            self.multiline = False
            return prompt(u"", multiline=True, **self.prompt_args)
        else:
            return prompt(u"> ", **self.prompt_args)

    def execute_cypher(self, source):
        with self.driver.session() as session:
            self.result_format(session.run(source)).print_result()

    def execute_command(self, source):
        assert source
        terms = shlex.split(source)
        command_name = terms[0]
        try:
            command = self.commands[command_name]
        except KeyError:
            click.secho("Unknown command: " + command_name, fg="yellow", err=True)
        else:
            command(terms)

    def set_multiline(self, args):
        self.multiline = True

    @classmethod
    def help(cls, args):
        print(HELP)

    @classmethod
    def exit(cls, args):
        exit(0)
