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

import click
from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from pygments.lexers.graph import CypherLexer

from .data import SeparatedValues
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


class Console(object):

    multiline = False
    watcher = None

    def __init__(self, uri, auth, verbose=False):
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
        self.data_writer = SeparatedValues(field_separator="\t", record_separator="\r\n")
        self.uri = uri
        if verbose:
            from .watcher import watch
            self.watcher = watch("neo4j.bolt")

    def loop(self):
        print(WELCOME.format(self.uri))
        while True:
            try:
                source = self.read().lstrip()
            except EOFError:
                return 0
            if source.startswith("/"):
                self.run_command(source)
            elif source:
                try:
                    self.run_cypher(source)
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

    def run_cypher(self, source):
        with self.driver.session() as session:
            self.data_writer.write_result(session.run(source))

    def run_command(self, source):
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
