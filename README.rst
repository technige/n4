==
N4
==

N4 is a Cypher runner and interactive console for Neo4j.


Installation
============

To install the latest stable version, simply run::

    pip install n4

For a specific version, such as an older version or beta, use::

    pip install n4==x.y.z

For the latest, bleeding edge code (possibly unstable), use::

    pip install git+https://github.com/technige/n4.git


This installs an ``n4`` executable onto your path along with a supplementary auth management tool, ``n4a``.


Executable: ``n4``
==================

Synopsis
--------
::

    n4 [OPTIONS] [STATEMENT]...

Options
-------
- ``-U``, ``--uri`` ``TEXT``       Set the connection URI.
- ``-u``, ``--user`` ``TEXT``      Set the user.
- ``-p``, ``--password`` ``TEXT``  Set the password.
- ``-i``, ``--insecure``           Use unencrypted communication (no TLS).
- ``-v``, ``--verbose``            Show low level communication detail.
- ``--help``                       Show this message and exit.

Description
-----------
If command line arguments are provided, these are executed in order as
statements. If no arguments are provided, an interactive console is
presented.

Statements entered at the interactive prompt or as arguments can be
regular Cypher, transaction control keywords or slash commands. Multiple
Cypher statements can be entered on the same line separated by semicolons.
These will be executed within a single transaction.

For a handy Cypher reference, see the `Cypher reference card <https://neo4j.com/docs/cypher-refcard/current/>`_.

Transactions can be managed interactively. To do this, use the transaction
control keywords ``BEGIN``, ``COMMIT`` and ``ROLLBACK``.

Slash commands provide access to supplementary functionality.

- ``//``      to enter multiline mode (press ``[Esc][Enter]`` to run)
- ``/?``      for help
- ``/x``      to exit

Playback commands
-----------------
- ``/r FILE`` load and run a Cypher file in a read transaction
- ``/w FILE`` load and run a Cypher file in a write transaction

Formatting commands
-------------------
- ``/csv``    format output as comma-separated values
- ``/table``  format output in a table
- ``/tsv``    format output as tab-separated values

Information commands
--------------------
- ``/config`` show Neo4j server configuration
- ``/kernel`` show Neo4j kernel information


Executable: ``n4a``
===================

Synopsis
--------
::

    n4a add [OPTIONS] AUTH_FILE USER_NAME
    n4a list [OPTIONS] AUTH_FILE
    n4a remove [OPTIONS] AUTH_FILE USER_NAME
    n4a update [OPTIONS] AUTH_FILE USER_NAME

Options
-------
- ``-password`` ``TEXT``     Pass the password instead of prompting for it.
- ``--help``                 Show this message and exit.

Description
-----------

Note that unlike ``n4``, ``n4a`` operates directly on the server file system and not remotely.

*TODO*
