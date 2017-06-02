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


from os import getenv

import click

from .console import Console, ConsoleError

DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "password"


@click.command()
@click.option("-U", "--uri", default=getenv("NEO4J_URI", DEFAULT_NEO4J_URI))
@click.option("-u", "--user", default=getenv("NEO4J_USER", DEFAULT_NEO4J_USER))
@click.option("-p", "--password", default=getenv("NEO4J_PASSWORD", DEFAULT_NEO4J_PASSWORD))
@click.option("-f", "--format", type=click.Choice(["csv", "tsv", "table"]))
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("statement", default="")
def repl(statement, uri, user, password, format, verbose):
    try:
        console = Console(uri, auth=(user, password), verbose=verbose)

        if format == "csv":
            console.set_csv_result_writer()
        elif format == "tsv":
            console.set_tsv_result_writer()
        else:
            console.set_tabular_result_writer()

        if statement:
            console.run_cypher(statement, {})
            exit_status = 0
        else:
            exit_status = console.loop()

    except ConsoleError as e:
        click.secho(e.args[0], err=True, fg="yellow")
        exit_status = 1
    exit(exit_status)


if __name__ == "__main__":
    repl()
