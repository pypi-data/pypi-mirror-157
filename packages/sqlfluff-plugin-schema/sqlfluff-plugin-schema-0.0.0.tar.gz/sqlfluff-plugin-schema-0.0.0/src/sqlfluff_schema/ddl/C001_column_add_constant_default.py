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
    # Adding a column with **constant** `DEFAULT`

    !!! info ""
        Not needed for PostgreSQL 11 and later.

    ## Rationale

    Adding a column with a constant default value requires updating each row of the table.

    ``` postgresql
    ALTER TABLE foo ADD COLUMN bar TEXT DEFAULT 'baz';
    ```

    ## Alternative

    ``` postgresql
    ALTER TABLE foo ADD COLUMN bar TEXT;
    UPDATE TABLE foo SET bar = 'baz'; -- You might want to back-fill in batches
    ALTER TABLE foo ALTER COLUMN bar SET DEFAULT 'baz';
    ```

    ## Configuration

    The `force_enable` config key controls whether this rule is active. You can find the default value [here](../../config.md#defaults)
    """

    groups = ("all", "migrations", "ddl")
    config_keywords = ("force_enable",)
    lints = {(grammar.AddColumn, grammar.DefaultConstraint): "Adding a new column with a default is not allowed."}

    def _eval_postgres(self, context):
        if self.force_enable:
            return super()._eval_postgres(context)
