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

from datetime import datetime
import shlex
from os.path import expanduser
from timeit import default_timer as timer
from textwrap import dedent

import click
from neo4j.v1 import GraphDatabase, ServiceUnavailable, CypherError, TransactionError
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_dict
from pygments.lexers.graph import CypherLexer
from pygments.token import Token

from n4.table import Table
from .data import TabularResultWriter, CSVResultWriter, TSVResultWriter
from .meta import title, description, quick_help, full_help


HISTORY_FILE = expanduser("~/.n4_history")


class Console(object):

    multi_line = False
    watcher = None

    tx_colour = "yellow"
    err_colour = "reset"
    meta_colour = "blue"
    prompt_colour = "blue"

    def __init__(self, uri, auth, secure=True, verbose=False):
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth, encrypted=secure)
        except ServiceUnavailable as error:
            raise ConsoleError("Could not connect to {} ({})".format(uri, error))
        self.uri = uri
        self.history = FileHistory(HISTORY_FILE)
        self.prompt_args = {
            "history": self.history,
            "lexer": PygmentsLexer(CypherLexer),
        }
        self.result_writer = TabularResultWriter()
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

            "/csv": self.set_csv_result_writer,
            "/table": self.set_tabular_result_writer,
            "/tsv": self.set_tsv_result_writer,

            "/config": self.config,
            "/kernel": self.kernel,

        }
        self.session = None
        self.tx = None
        self.tx_counter = 0

    def loop(self):
        click.echo(title, err=True)
        click.echo("Connected to {}".format(self.uri).rstrip(), err=True)
        click.echo(err=True)
        click.echo(dedent(quick_help), err=True)
        while True:
            try:
                source = self.read().strip()
            except KeyboardInterrupt:
                continue
            except EOFError:
                return 0
            try:
                self.run(source)
            except ServiceUnavailable:
                return 1

    def run(self, source):
        try:
            if not source:
                pass
            elif source.startswith("/"):
                self.run_command(source)
            elif source.upper() == "BEGIN":
                self.begin_transaction()
            elif source.upper() == "COMMIT":
                self.commit_transaction()
            elif source.upper() == "ROLLBACK":
                self.rollback_transaction()
            elif self.tx is None:
                with self.driver.session() as session:
                    self.run_cypher(session, source, {})
            else:
                self.run_cypher(self.tx, source, {})
                self.tx_counter += 1
        except CypherError as error:
            if error.classification == "ClientError":
                pass
            elif error.classification == "DatabaseError":
                pass
            elif error.classification == "TransientError":
                pass
            else:
                pass
            click.secho("{}: {}".format(error.title, error.message), err=True)
        except TransactionError:
            click.secho("Transaction error", err=True, fg=self.err_colour)

    def rollback_transaction(self):
        if self.session:
            try:
                self.session.rollback_transaction()
                click.secho(u"(Transaction ROLLBACK at {})".format(datetime.now()),
                            err=True, fg=self.tx_colour, bold=True)
            finally:
                self.tx = None
                self.tx_counter = 0
                self.session.close()
                self.session = None
        else:
            click.secho(u"No current transaction", err=True, fg=self.err_colour)

    def commit_transaction(self):
        if self.session:
            try:
                self.session.commit_transaction()
                click.secho(u"(Transaction COMMIT at {})".format(datetime.now()),
                            err=True, fg=self.tx_colour, bold=True)
            finally:
                self.tx = None
                self.tx_counter = 0
                self.session.close()
                self.session = None
        else:
            click.secho(u"No current transaction", err=True, fg=self.err_colour)

    def begin_transaction(self):
        if self.tx is None:
            self.session = self.driver.session()
            self.tx = self.session.begin_transaction()
            self.tx_counter = 1
            click.secho(u"(Transaction BEGIN at {})".format(datetime.now()),
                        err=True, fg=self.tx_colour, bold=True)
        else:
            click.secho(u"Transaction already open", err=True, fg=self.err_colour)

    def read(self):
        if self.multi_line:
            self.multi_line = False
            return prompt(u"", multiline=True, **self.prompt_args)

        example_style = style_from_dict({
            Token.Prompt: "#ansi{}".format(self.prompt_colour),
            Token.TxCounter: "#ansi{} bold".format(self.tx_colour),
        })

        def get_prompt_tokens(_):
            tokens = []
            if self.tx is None:
                tokens.append((Token.Prompt, "\n-> "))
            else:
                tokens.append((Token.Prompt, "\n-("))
                tokens.append((Token.TxCounter, "{}".format(self.tx_counter)))
                tokens.append((Token.Prompt, ")-> "))
            return tokens

        return prompt(get_prompt_tokens=get_prompt_tokens, style=example_style, **self.prompt_args)

    def run_cypher(self, context, statement, parameters):
        t0 = timer()
        result = context.run(statement, parameters)
        total = 0
        if result.keys():
            self.result_writer.write_header(result)
            more = True
            while more:
                total += self.result_writer.write(result, 50)
                more = result.peek() is not None
        summary = result.summary()
        t1 = timer() - t0
        if len(summary.server.address) == 4:  # IPv6
            server_address = "[{}]:{}".format(*summary.server.address)
        else:                                 # IPv4
            server_address = "{}:{}".format(*summary.server.address)
        click.secho(u"({} record{} from {} in {:.3f}s)".format(
            total, "" if total == 1 else "s", server_address, t1),
            err=True, fg=self.meta_colour, bold=True)

    def run_command(self, source):
        assert source
        terms = shlex.split(source)
        command_name = terms[0]
        try:
            command = self.commands[command_name]
        except KeyError:
            click.secho("Unknown command: " + command_name, err=True, fg=self.err_colour)
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
        click.echo(description, err=True)
        click.echo(err=True)
        click.echo(full_help.replace("\b\n", ""), err=True)

    @classmethod
    def exit(cls, **kwargs):
        exit(0)

    def set_csv_result_writer(self, **kwargs):
        self.result_writer = CSVResultWriter()

    def set_tabular_result_writer(self, **kwargs):
        self.result_writer = TabularResultWriter()

    def set_tsv_result_writer(self, **kwargs):
        self.result_writer = TSVResultWriter()

    def config(self, **kwargs):
        with self.driver.session() as session:
            result = session.run("CALL dbms.listConfig")
            table = None
            last_category = None
            for record in result:
                name = record["name"]
                category, _, _ = name.partition(".")
                if category != last_category:
                    if table is not None:
                        table.echo(header_style={"fg": "cyan"})
                        click.echo()
                    table = Table(["name", "value"], field_separator=u" = ", padding=0, auto_align=False, header=0)
                table.append((name, record["value"]))
                last_category = category
            table.echo(header_style={"fg": self.meta_colour})

    def kernel(self, **kwargs):
        with self.driver.session() as session:
            result = session.run("CALL dbms.queryJmx", {"query": "org.neo4j:instance=kernel#0,name=Kernel"})
            table = Table(["key", "value"], field_separator=u" = ", padding=0, auto_align=False, header=0)
            for record in result:
                attributes = record["attributes"]
                for key, value_dict in sorted(attributes.items()):
                    value = value_dict["value"]
                    if key.endswith("Date") or key.endswith("Time"):
                        try:
                            value = datetime.fromtimestamp(value / 1000).isoformat(" ")
                        except:
                            pass
                    table.append((key, value))
            table.echo(header_style={"fg": self.meta_colour})


class ConsoleError(Exception):

    pass
