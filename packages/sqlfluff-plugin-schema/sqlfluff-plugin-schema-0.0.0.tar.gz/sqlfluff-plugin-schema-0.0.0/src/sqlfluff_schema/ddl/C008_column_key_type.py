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
from sqlfluff_schema.selectors import select
from sqlfluff_schema.utils import first


class Rule(PostgresRule):
    """
    # Adding an `INT` column with `PRIMARY KEY` or `REFERENCES`

    ## Rationale

    ### Integers
    You might exceed the maximum for an integer `INTEGER` if you have a large table.
    If you have a small table, then the overhead from using a `BIGINT` wouldn't matter much,
    and will save you the pain of migrating to a `BIGINT` should your become larger in the future.

    ### UUID
    Do not use a `TEXT` type to store UUID-compatible values.

    ## Alternative
    ### Integers
    You should always use `BIGINT` or `BIGSERIAL` instead of `INTEGER` for columns acting as primary keys, or referencing other
    primary keys.

    ### UUID
    Postgres has native support for the `UUID` type.

    ## Configuration

    The `allowed_key_types` config key controls which types are allowed. You can find the default value [here](../../config.md#defaults)
    """

    groups = ("all", "migrations", "ddl")
    config_keywords = ["allowed_key_types"]
    lints = {
        (grammar.AddColumn, grammar.PrimaryKey): "Using integers for primary keys is not allowed.",
        (grammar.AddColumn, grammar.References): "Using integers for foreign keys is not allowed.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_key_types = {col.strip() for col in self.allowed_key_types.split(",")}

    def _eval_postgres_lint(self, lint, segment, dialect):
        if super()._eval_postgres_lint(lint, segment, dialect):
            if not first(select(segment, "data_type")) in self.allowed_key_types:
                return True
        return False
