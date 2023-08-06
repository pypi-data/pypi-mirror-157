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
    # Dropping Columns

    ## Rationale

    When deploying the new application code that removes an existing column, the existing application instances
    referencing the (now removed) column will raise errors when interacting with the table.

    ## Alternative

    1. Remove references to the column from the application code
    2. Deploy the new code
    3. Drop the column
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.DropColumn: "Dropping columns is not allowed."}
