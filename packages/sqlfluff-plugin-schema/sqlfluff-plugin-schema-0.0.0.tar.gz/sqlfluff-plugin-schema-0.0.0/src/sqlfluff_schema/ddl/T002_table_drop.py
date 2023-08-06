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
    # Dropping tables on production

    ## Rationale

    Dropping tables on production.

    ## Alternative

    Do not drop tables on production.
    """

    groups = ("all", "migrations", "ddl")
    lints = {grammar.DropTable: "Dropping tables is not allowed."}
