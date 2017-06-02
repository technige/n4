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
from timeit import default_timer as timer

import click
from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from pygments.lexers.graph import CypherLexer

from .data import CommaSeparatedValues, TabSeparatedValues, DataTable
from .meta import __version__


HELP = """\
N4 is an interactive Cypher environment for use with Neo4j.

Type Cypher statements at the prompt and press [Enter] to run.

General commands:
  //  to enter multi-line mode (press [Alt]+[Enter] to run)
  /?  for help
  /x  to exit

Formatting commands:
  /csv    format output as comma-separated values
  /table  format output in a table
  /tsv    format output as tab-separated values

Report bugs to n4@nige.tech\
"""
HISTORY_FILE = expanduser("~/.n4_history")
WELCOME = """\
N4 v{} -- Console for Neo4j
Connected to {{}}

//  to enter multi-line mode (press [Alt]+[Enter] to run)
/?  for help
/x  to exit
""".format(__version__)


class Console(object):

    multi_line = False
    watcher = None
    statements = None

    def __init__(self, uri, auth, verbose=False):
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
        except ServiceUnavailable:
            raise ConsoleError("Could not connect to {}".format(uri))
        self.uri = uri
        self.history = FileHistory(HISTORY_FILE)
        self.prompt_args = {
            "history": self.history,
            "lexer": PygmentsLexer(CypherLexer),
        }
        self.data_writer = DataTable()
        if verbose:
            from .watcher import watch
            self.watcher = watch("neo4j.bolt")

        self.commands = {

            "//": self.set_multi_line,

            "/?": self.help,
            "/h": self.help,
            "/help": self.help,

            "/x": self.exit,
            "/exit": self.exit,

            "/csv": self.set_csv_data_writer,
            "/table": self.set_table_data_writer,
            "/tsv": self.set_tsv_data_writer,

        }
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def loop(self):
        print(WELCOME.format(self.uri))
        while True:
            try:
                source = self.read().lstrip()
            except KeyboardInterrupt:
                continue
            except EOFError:
                return 0
            if source.startswith("/"):
                self.run_command(source)
            elif source:
                try:
                    self.run_cypher(source, {})
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
        if self.multi_line:
            self.multi_line = False
            return prompt(u"", multiline=True, **self.prompt_args)
        elif self.statements is None:
            return prompt(u"~> ", **self.prompt_args)
        else:
            return prompt(u"{}> ".format(len(self.statements) + 1), **self.prompt_args)

    def run_cypher(self, statement, parameters):
        if self.statements is None:
            self.run_autocommit_transaction(statement, parameters)
        else:
            self.statements.append((statement, parameters))

    def run_autocommit_transaction(self, statement, parameters):
        with self.driver.session() as session:
            t0 = timer()
            result = session.run(statement, parameters)
            total = 0
            if result.keys():
                more = True
                while more:
                    total += self.data_writer.write_result(result)
                    more = result.peek() is not None
            summary = result.summary()
            t1 = timer() - t0
            server_address = "{}:{}".format(*summary.server.address)
            click.secho(u"({} record{} from {} in {:.3f}s)".format(
                total, "" if total == 1 else "s", server_address, t1),
                err=True, fg="cyan")

    def run_command(self, source):
        assert source
        terms = shlex.split(source)
        command_name = terms[0]
        try:
            command = self.commands[command_name]
        except KeyError:
            click.secho("Unknown command: " + command_name, fg="yellow", err=True)
        else:
            kwargs = {}
            for term in terms[1:]:
                key, _, value = term.partition("=")
                kwargs[key] = value
            command(**kwargs)

    def set_multi_line(self, **kwargs):
        self.multi_line = True

    @classmethod
    def help(cls, **kwargs):
        click.echo(HELP, err=True)

    @classmethod
    def exit(cls, **kwargs):
        exit(0)

    def set_csv_data_writer(self, **kwargs):
        self.data_writer = CommaSeparatedValues(header=kwargs.get("header", 1))

    def set_table_data_writer(self, **kwargs):
        self.data_writer = DataTable(header=kwargs.get("header", 1),
                                     page_limit=kwargs.get("page_limit", 50),
                                     page_gap=kwargs.get("page_gap", 1))

    def set_tsv_data_writer(self, **kwargs):
        self.data_writer = TabSeparatedValues(header=kwargs.get("header", 1))


class ConsoleError(Exception):

    pass
