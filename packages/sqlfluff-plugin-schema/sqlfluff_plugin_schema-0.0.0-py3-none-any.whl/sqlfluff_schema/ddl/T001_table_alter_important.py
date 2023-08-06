# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlfluff.core.rules.base import LintResult

from sqlfluff_schema.core import PostgresRule


class Rule(PostgresRule):
    """
    # Making changes to certain tables

    ## Rationale

    Some core tables are more critical than others, and sometimes it is better to minimize operations on them.

    ## Configuration
    The `forbidden_tables` config key controls which tables should be disallowed.
    You can find the default value [here](../../config.md#defaults)
    """

    groups = ("all", "migrations", "ddl")
    config_keywords = ("forbidden_tables",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forbidden_tables = {col.strip() for col in self.forbidden_tables.split(",")}

    def _eval_postgres(self, context):
        segment = context.segment

        if segment.is_type("alter_table_statement"):
            for seg in segment.segments:
                if not seg.is_type("table_reference"):
                    continue
                table_name = seg.raw.lower()
                if table_name not in self.forbidden_tables:
                    return
                return LintResult(
                    anchor=seg,
                    description=f"Altering table `{table_name}` is not allowed.",
                )
