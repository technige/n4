# N4

N4 is a Cypher runner and interactive console for Neo4j.

## Usage

### Installation

To install N4, simply run:
```
pip install n4
```

This installs an `n4` executable onto your path.

### Synopsis
```
n4 [OPTIONS] [STATEMENT]...
```

### Options
- `-U`, `--uri` `TEXT`       Set the connection URI.
- `-u`, `--user` `TEXT`      Set the user.
- `-p`, `--password` `TEXT`  Set the password.
- `-i`, `--insecure`       Use unencrypted communication (no TLS).
- `-v`, `--verbose`        Show low level communication detail.
- `--help`               Show this message and exit.

### Description
If command line arguments are provided, these are executed in order as
statements. If no arguments are provided, an interactive console is
presented. Statements entered at the interactive prompt or as arguments
can be regular Cypher, transaction control keywords or slash commands.

For a handy Cypher reference, see the [Cypher reference card](https://neo4j.com/docs/cypher-refcard/current/).

Transactions can be managed interactively. To do this, use the transaction
control keywords `BEGIN`, `COMMIT` and `ROLLBACK`.

Slash commands provide access to supplementary functionality.

- `//`      to enter multiline mode (press `[Esc][Enter]` to run)
- `/?`      for help
- `/x`      to exit

### Formatting commands
- `/csv`    format output as comma-separated values
- `/table`  format output in a table
- `/tsv`    format output as tab-separated values

### Information commands
- `/config` show Neo4j server configuration
- `/kernel` show Neo4j kernel information
