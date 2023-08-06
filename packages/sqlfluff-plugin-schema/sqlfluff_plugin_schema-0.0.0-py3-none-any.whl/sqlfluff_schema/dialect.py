# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlfluff.core.parser import BaseSegment, Ref, Sequence
from sqlfluff.dialects import dialect_postgres as postgres


class SavepointStatementSegment(BaseSegment):
    type = "savepoint_statement"
    match_grammar = Sequence("SAVEPOINT", Ref("SingleIdentifierGrammar"))


def patch():
    postgres.postgres_dialect.add(SavepointStatementSegment=SavepointStatementSegment)
    postgres.StatementSegment.parse_grammar = postgres.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("SavepointStatementSegment"),
        ],
    )
