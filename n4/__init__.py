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


from __future__ import print_function

from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict

from pygments.lexers.graph import CypherLexer
from pygments.token import Token

from .meta import __version__, history_file


STYLE = style_from_dict({
    Token.Border: "#808080",
    Token.Error: "#ffff00",
})


class Console(object):

    def __init__(self, uri, auth):
        print("N4 v{}".format(__version__))
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.history = FileHistory(history_file)
        self.prompt_args = {
            "history": self.history,
            "lexer": PygmentsLexer(CypherLexer),
        }

    def read(self):
        source = self.read_line().lstrip()
        if source == "//":
            print_tokens([
                (Token.Border, u"--------->--------->--------->--------->--------->------[<Esc><Enter>]--"),
                (Token, '\n'),
            ], style=STYLE)
            source = self.read_block()
            print_tokens([
                (Token.Border, u"------------------------------------------------------------------------"),
                (Token, '\n'),
            ], style=STYLE)
        return source

    def read_line(self):
        return prompt(u"> ", **self.prompt_args)

    def read_block(self):
        return prompt(u"", multiline=True, **self.prompt_args)

    def execute_cypher(self, source):
        with self.driver.session() as session:
            result = session.run(source)
            for record in result:
                print(record)

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
