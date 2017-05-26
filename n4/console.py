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

from os.path import expanduser
from time import perf_counter

from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict

from pygments.lexers.graph import CypherLexer
from pygments.token import Token

from .meta import __version__


EOL = u"\r\n"
HISTORY_FILE = expanduser("~/.n4_history")
STYLE = style_from_dict({
    Token.Border: "#808080",
    Token.Error: "#ffff00",
    Token.Metadata: "#00ffff",
})


class Console(object):

    def __init__(self, uri, auth):
        print("N4 v{}".format(__version__))
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.history = FileHistory(HISTORY_FILE)
        self.prompt_args = {
            "history": self.history,
            "lexer": PygmentsLexer(CypherLexer),
        }

    def read(self):
        source = self.read_line().lstrip()
        if source == "//":
            print_tokens([
                (Token.Border, u"--------->--------->--------->--------->--------->------[<Esc><Enter>]--"),
                (Token, EOL),
            ], style=STYLE)
            source = self.read_block()
            print_tokens([
                (Token.Border, u"------------------------------------------------------------------------"),
                (Token, EOL),
            ], style=STYLE)
        return source

    def read_line(self):
        return prompt(u"> ", **self.prompt_args)

    def read_block(self):
        return prompt(u"", multiline=True, **self.prompt_args)

    def execute_cypher(self, source):
        with self.driver.session() as session:
            result = session.run(source)
            count, time = self.print_result(result)
            self.print_result_summary(count, time, result.summary())

    def print_result(self, result):
        count = 0
        t0 = perf_counter()
        print_tokens([(Token.Metadata, "\t".join(result.keys())), (Token, EOL)], style=STYLE)
        for count, record in enumerate(result):
            print("\t".join(map(str, record.values())))
        return count, perf_counter() - t0

    def print_result_summary(self, count, time, summary):
        server_address = "{}:{}".format(*summary.server.address)
        print_tokens([
            (Token.Metadata, u"({} record{} from {} in {:.3f}s)".format(count, "" if count == 1 else "s", server_address, time)),
            (Token, EOL),
        ], style=STYLE)

    def execute_command(self, source):
        if source == "/?":
            print("HELP!!")
        elif source == "/x":
            exit(0)
        else:
            self.print_error("Unknown command: " + source)

    def loop(self):
        while True:
            try:
                source = self.read()
            except EOFError:
                return 0
            if source.startswith("/"):
                self.execute_command(source)
            else:
                try:
                    self.execute_cypher(source)
                except CypherError as error:
                    self.print_error(error.message)
                except ServiceUnavailable:
                    return 1

    def print_error(self, message):
        print_tokens([(Token.Error, message), (Token, "\n")], style=STYLE)
