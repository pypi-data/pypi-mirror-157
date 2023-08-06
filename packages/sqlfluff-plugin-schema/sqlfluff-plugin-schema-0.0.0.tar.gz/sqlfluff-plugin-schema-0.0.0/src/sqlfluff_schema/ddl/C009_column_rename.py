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
    # Renaming columns

    ## Rationale

    When deploying the new application code that references the new name, the existing application instances
    referencing the old name will raise errors when interacting with the old column.

    ## Alternative

    1. Add a new column with the new name
    2. Add triggers on the old column to sync the new column when inserts/updates occur happen on the original column
    3. Copy over the existing data from the original column
    4. Drop the original column
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.RenameColumn: "Renaming columns is not allowed."}
