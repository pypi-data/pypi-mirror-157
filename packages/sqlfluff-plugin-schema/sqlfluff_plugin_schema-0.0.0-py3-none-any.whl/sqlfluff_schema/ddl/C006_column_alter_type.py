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
    # Altering column `TYPE`

    ## Rationale

    > Adding a column with a volatile `DEFAULT` or changing the type of an existing column will require the entire table and its indexes
    > to be rewritten. As an exception, when changing the type of an existing column, if the `USING` clause does not change the column
    > contents and the old type is either binary coercible to the new type or an unconstrained domain over the new type,
    > a table rewrite is not needed; but any indexes on the affected columns must still be rebuilt.
    > Table and/or index rebuilds may take a significant amount of time for a large table;
    > and will temporarily require as much as double the disk space.
    > [[ref]](https://www.postgresql.org/docs/current/sql-altertable.html)

    ## Alternative

    1. Add a new column with the new type
    2. Add triggers on the original column to sync the new column when inserts/updates occur happen on the original column
    3. Copy over the existing data from the original column
    4. Drop the original column
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.AlterColumnType: "Altering a column type is not allowed."}
