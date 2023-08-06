# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from collections import defaultdict

from sqlfluff.core.rules.base import LintResult

from sqlfluff_schema import grammar
from sqlfluff_schema.core import PostgresRule
from sqlfluff_schema.selectors import select
from sqlfluff_schema.utils import first


class Rule(PostgresRule):
    """
    # Altering multiple tables in a single transaction

    """

    groups = ("all", "migrations", "ddl")

    def _eval_postgres(self, context):
        segment = context.segment
        memory = context.memory

        db = memory.setdefault("tables", defaultdict(set))
        if segment.is_type("transaction_statement"):
            memory.setdefault("depth", -1)
            kw = set(select(segment, "keyword", raw=True))
            if kw.intersection(grammar.TXN_BEGIN_KEYWORDS):
                memory["depth"] += 1
            elif kw.intersection(grammar.TXN_END_KEYWORDS):
                memory["tables"].pop(memory["depth"], None)
                memory["depth"] -= 1
            return LintResult(memory=memory)

        if not segment.is_type("alter_table_statement"):
            return LintResult(memory=memory)

        table = first(select(segment, "table_reference", raw=True), None)
        # a table reference wouldn't exist for cases like `ALTER TABLE ALL IN TABLESPACE ...`
        if table is None:
            return LintResult(memory=memory)

        depth = memory.get("depth", -1)
        db[depth].add(table)

        if any(depth >= 0 and len(tables) > 1 for depth, tables in db.items()):
            return LintResult(anchor=segment, memory=memory, description="Altering multiple tables in a single transaction is not allowed.")

        return LintResult(memory=memory)
