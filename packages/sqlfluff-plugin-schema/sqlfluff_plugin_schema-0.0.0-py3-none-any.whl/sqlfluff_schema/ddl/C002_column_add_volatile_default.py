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
    # Adding a column with **volatile** `DEFAULT`

    !!! danger "Volatility"
        We cannot accurately determine which value is volatile, and which is not.
        To err on the safe side, we have chosen to fail on anything other than literals, and it is up
        to the user to manually override on a case-by-case basis.

        ```postgresql
        ALTER TABLE foo ADD COLUMN bar TIMESTAMP DEFAULT <value>; -- noqa: DDL_C002
        ```

    ## Rationale

    > Adding a column with a volatile `DEFAULT` or changing the type of an existing column will require the entire table and its indexes
    > to be rewritten. As an exception, when changing the type of an existing column, if the `USING` clause does not change the column
    > contents and the old type is either binary coercible to the new type or an unconstrained domain over the new type,
    > a table rewrite is not needed; but any indexes on the affected columns must still be rebuilt.
    > Table and/or index rebuilds may take a significant amount of time for a large table;
    > and will temporarily require as much as double the disk space.
    > [[ref]](https://www.postgresql.org/docs/current/sql-altertable.html)

    ``` postgresql
    ALTER TABLE foo ADD COLUMN bar TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ```

    ## Alternative

    ``` postgresql
    ALTER TABLE foo ADD COLUMN bar TIMESTAMP NULL;
    UPDATE TABLE foo SET bar = CURRENT_TIMESTAMP; -- You might want to back-fill in batches
    ALTER TABLE foo ALTER COLUMN bar SET DEFAULT CURRENT_TIMESTAMP;
    ```

    For non-nullable columns, check [`C005_column_alter_not_null`][sqlfluff_schema.ddl.C005_column_alter_not_null]
    """

    groups = ("all", "migrations", "ddl")
    lints = {(grammar.AddColumn, grammar.VolatileDefaultConstraint): "Adding a new column with a volatile default is not allowed."}
