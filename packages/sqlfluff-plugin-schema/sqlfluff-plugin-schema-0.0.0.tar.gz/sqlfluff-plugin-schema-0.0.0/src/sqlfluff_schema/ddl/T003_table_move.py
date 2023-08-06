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
    # Moving tables

    ## Rationale

    The table(s) are locked while the data files are being physically moved to the new tablespace.

    ``` postgresql
    ALTER TABLE foo SET TABLESPACE bar;
    ALTER TABLE ALL IN TABLESPACE foo SET TABLESPACE bar;
    ```

    ## Alternative

    1. Create a new table
    2. Add triggers on the old table to sync the new table when inserts/updates occur happen on the original table
    3. Copy over the existing data from the original table
    4. Drop the original table
    """

    groups = ("all", "migrations", "ddl")
    lints = {
        grammar.SetTableSpace: "Altering tablespace is not allowed.",
        grammar.SetAllTableSpace: "Altering tablespace is not allowed.",
    }
