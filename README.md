# N4: Cypher Console for Neo4j

N4 is an interactive Cypher environment for use with Neo4j.


## Installation
To install N4, simply run:
```
pip install n4
```

This installs an `n4` executable onto your path.


## Usage
```
Usage: n4 [OPTIONS] [STATEMENT]...

  Cypher runner and interactive console for use with Neo4j.

  If STATEMENT arguments are provided, these are executed in order as if
  entered at the interactive prompt. These arguments can include slash
  commands. If no STATEMENT arguments are provided, an interactive console
  is presented.

Options:
  -U, --uri TEXT       Set the connection URI.
  -u, --user TEXT      Set the user.
  -p, --password TEXT  Set the password.
  -i, --insecure       Use unencrypted communication (no TLS).
  -v, --verbose        Show low level communication detail.
  --help               Show this message and exit.
```


### Command Line Options
TODO

### Slash Commands


## Running Cypher
TODO (autocommit)


## Slash Commands
Special console commands start with a slash character (`/`) and are used to access functionality outside of direct Cypher execution.

### General Commands
- `//`      to enter multiline mode (press `[Esc][Enter]` to run)
- `/?`      for help
- `/x`      to exit

### Formatting Commands
- `/csv`    format output as comma-separated values
- `/table`  format output in a table
- `/tsv`    format output as tab-separated values

### Information Commands
- `/config` show Neo4j server configuration
- `/kernel` show Neo4j kernel information
