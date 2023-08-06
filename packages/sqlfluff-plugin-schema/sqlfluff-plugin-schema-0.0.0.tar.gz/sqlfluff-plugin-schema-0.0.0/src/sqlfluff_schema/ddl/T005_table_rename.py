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
    # Renaming tables

    ## Rationale

    When deploying the new application code that references the new name, the existing application instances
    referencing the old name will raise errors when interacting with the old table.

    ## Alternative

    1. Create a new table
    2. Add triggers on the old table to sync the new table when inserts/updates occur happen on the original table
    3. Copy over the existing data from the original table
    4. Drop the original table
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.RenameTable: "Renaming tables is not allowed."}
