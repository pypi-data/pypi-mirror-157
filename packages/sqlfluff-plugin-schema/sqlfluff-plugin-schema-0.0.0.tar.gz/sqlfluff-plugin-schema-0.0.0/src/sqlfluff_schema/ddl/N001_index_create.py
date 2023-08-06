# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlfluff_schema import grammar
from sqlfluff_schema.core import PostgresRule


class Rule(PostgresRule):
    """
    # Creating indexes

    ## Rationale

    > Creating an index can interfere with regular operation of a database.
    > Normally PostgreSQL locks the table to be indexed against writes
    > and performs the entire index build with a single scan of the table.
    > Other transactions can still read the table, but if they try to insert, update, or delete rows in the table
    > they will block until the index build is finished. This could have a severe effect
    > if the system is a live production database.
    > Very large tables can take many hours to be indexed,
    > and even for smaller tables, an index build can lock out writers for periods that are unacceptably long
    > for a production system.
    > [[ref]](https://www.postgresql.org/docs/current/sql-createindex.html)

    ``` postgresql
    CREATE INDEX title_idx ON films (title);
    ```

    ## Alternative

    ``` postgresql
    CREATE INDEX CONCURRENTLY title_idx ON films (title);
    ```
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.CreateIndexBlocking: "Creating an index without `CONCURRENTLY` is not allowed."}
