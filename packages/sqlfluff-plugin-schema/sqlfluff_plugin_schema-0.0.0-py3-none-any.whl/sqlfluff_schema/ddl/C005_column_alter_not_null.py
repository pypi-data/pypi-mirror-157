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
    # Setting `NOT NULL` on an existing column

    ## Rationale

    The database does a table scan to verify all existing values are not null,
    while holding an exclusive lock.

    ``` postgresql
    ALTER TABLE foo ALTER bar SET NOT NULL;
    ```

    ## Alternative

    !!! info ""
        PostgreSQL 12 or later

    ``` postgresql
    ALTER TABLE foo ADD CONSTRAINT constr CHECK (bar IS NOT NULL) NOT VALID;
    ALTER TABLE foo VALIDATE CONSTRAINT constr;
    ALTER TABLE foo ALTER COLUMN bar SET NOT NULL; -- noqa DDL_C005
    ALTER TABLE foo DROP CONSTRAINT constr;
    ```
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.AlterColumnNotNull: "not allowed."}
