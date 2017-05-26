#!/usr/bin/env python


from __future__ import print_function

from os import getenv
from os.path import expanduser

from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict

from pygments.lexers.graph import CypherLexer
from pygments.token import Token

__version__ = "1.0.0a1"

HISTORY_FILE = expanduser("~/.n4_history")
STYLE = style_from_dict({
    Token.Border: "#808080",
    Token.Error: "#ffff00",
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


def main():
    scheme = "bolt"
    host = "localhost"
    port = 7687
    uri = getenv("NEO4J_URI", "%s://%s:%d" % (scheme, host, port))
    user = getenv("NEO4J_USER", "neo4j")
    password = getenv("NEO4J_PASSWORD", "password")
    auth = (user, password)
    console = Console(uri, auth=auth)
    exit(console.loop())


if __name__ == "__main__":
    main()
