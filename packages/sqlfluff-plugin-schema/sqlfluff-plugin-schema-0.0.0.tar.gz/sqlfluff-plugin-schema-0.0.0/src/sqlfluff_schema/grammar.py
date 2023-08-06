# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlfluff.core.parser import AnyNumberOf, Bracketed, Delimited, OneOf, OptionallyBracketed, Ref, Sequence
from sqlfluff.core.parser.grammar.base import BaseGrammar
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.dialects.dialect_postgres import postgres_dialect as pg


class Not(BaseGrammar):
    def __init__(self, wrapped, *args, **kwargs):
        self.wrapped = wrapped
        super(Not, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        res = self.wrapped.match(segments, parse_context)
        return MatchResult(res.unmatched_segments, res.matched_segments)


class RenameTable:
    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Delimited(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
                Ref("TableReferenceSegment"),
                Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
            ),
        ),
    )


class DropColumn:
    type = "alter_table_action_segment"
    match_grammar = Sequence(
        "DROP",
        Ref.keyword("COLUMN", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("ColumnReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class RenameColumn:
    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Delimited(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
                Ref.keyword("ONLY", optional=True),
                Ref("TableReferenceSegment"),
                Ref("StarSegment", optional=True),
                Sequence(
                    "RENAME",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnReferenceSegment"),
                    "TO",
                    Ref("ColumnReferenceSegment"),
                ),
            ),
        ),
    )


class NonCombinableAlterTable:
    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Delimited(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
                Ref("TableReferenceSegment"),
                OneOf(
                    Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
                    Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
                    Sequence(
                        "ATTACH",
                        "PARTITION",
                        Ref("ParameterNameSegment"),
                        OneOf(
                            Sequence("FOR", "VALUES", Ref("PartitionBoundSpecSegment")),
                            "DEFAULT",
                        ),
                    ),
                    Sequence(
                        "DETACH",
                        "PARTITION",
                        Ref("ParameterNameSegment"),
                        Ref.keyword("CONCURRENTLY", optional=True),
                        Ref.keyword("FINALIZE", optional=True),
                    ),
                ),
            ),
        ),
    )


class SetAllTableSpace:
    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Delimited(
            Sequence(
                "ALL",
                "IN",
                "TABLESPACE",
                Ref("ParameterNameSegment"),
                Sequence(
                    "OWNED",
                    "BY",
                    Delimited(Ref("ObjectReferenceSegment"), delimiter=Ref("CommaSegment")),
                    optional=True,
                ),
                "SET",
                "TABLESPACE",
                Ref("ParameterNameSegment"),
                Ref.keyword("NOWAIT", optional=True),
            ),
        ),
    )


class SetTableSpace:
    type = "alter_table_action_segment"
    match_grammar = Sequence(
        "SET",
        "TABLESPACE",
        Ref("ParameterNameSegment"),
    )


DropTable = pg.get_segment("DropTableStatementSegment")


class AddColumn:
    type = "alter_table_action_segment"
    match_grammar = Sequence(
        "ADD",
        Ref.keyword("COLUMN", optional=True),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ColumnReferenceSegment"),
        Ref("DatatypeSegment"),
    )


class DefaultConstraint:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "DEFAULT",
            OneOf(Ref("LiteralGrammar"), Ref("FunctionSegment"), Ref("BareFunctionSegment"), Ref("ExpressionSegment")),
        ),
    )


class LiteralDefaultConstraint:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "DEFAULT",
            Ref("LiteralGrammar"),
        ),
    )


class VolatileDefaultConstraint:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "DEFAULT",
            Not(Ref("LiteralGrammar")),
        ),
    )


class PrimaryKey:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Ref("PrimaryKeyGrammar"),
    )


class References:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Ref("ReferenceDefinitionGrammar"),
    )


class ForeignKey:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Ref("ForeignKeyGrammar"),
    )


class Unique:
    type = "column_constraint_segment"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        "UNIQUE",
    )


class AlterColumnType:
    type = "alter_table_action_segment"
    match_grammar = Sequence(
        "ALTER",
        Ref.keyword("COLUMN", optional=True),
        Ref("ColumnReferenceSegment"),
        Sequence(
            Sequence("SET", "DATA", optional=True),
            "TYPE",
            Ref("DatatypeSegment"),
            Sequence("COLLATE", Ref("QuotedLiteralSegment"), optional=True),
            Sequence("USING", OneOf(Ref("ExpressionSegment")), optional=True),
        ),
    )


class AlterColumnNotNull:
    type = "alter_table_action_segment"
    match_grammar = Sequence(
        "ALTER",
        Ref.keyword("COLUMN", optional=True),
        Ref("ColumnReferenceSegment"),
        Ref.keyword("SET", optional=True),
        "NOT",
        "NULL",
    )


class AlterTableConstraint:
    type = "alter_table_action_segment"
    match_grammar = Sequence("ADD", Ref("TableConstraintSegment"), Sequence("NOT", "VALID", optional=True))


class AlterTableInvalidConstraint:
    type = "alter_table_action_segment"
    match_grammar = Sequence("ADD", Ref("TableConstraintSegment"), "NOT", "VALID")


class CreateIndexBlocking:
    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("UNIQUE", optional=True),
        Ref("OrReplaceGrammar", optional=True),
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment", optional=True),
        "ON",
        Ref.keyword("ONLY", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("USING", Ref("FunctionSegment"), optional=True),
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnReferenceSegment"),
                            OptionallyBracketed(Ref("FunctionSegment")),
                            Bracketed(Ref("ExpressionSegment")),
                        ),
                        AnyNumberOf(
                            Sequence(
                                "COLLATE",
                                OneOf(
                                    Ref("LiteralGrammar"),
                                    Ref("QuotedIdentifierSegment"),
                                ),
                            ),
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Bracketed(
                                    Delimited(
                                        Sequence(
                                            Ref("ParameterNameSegment"),
                                            Ref("EqualsSegment"),
                                            OneOf(
                                                Ref("LiteralGrammar"),
                                                Ref("QuotedIdentifierSegment"),
                                            ),
                                        ),
                                        delimiter=Ref("CommaSegment"),
                                    ),
                                ),
                            ),
                            OneOf("ASC", "DESC"),
                            OneOf(Sequence("NULLS", "FIRST"), Sequence("NULLS", "LAST")),
                        ),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        AnyNumberOf(
            Sequence(
                "INCLUDE",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"), delimiter=Ref("CommaSegment"))),
            ),
            Sequence(
                "WITH",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Ref("EqualsSegment"),
                            Ref("LiteralGrammar"),
                        ),
                        delimiter=Ref("CommaSegment"),
                    )
                ),
            ),
            Sequence("TABLESPACE", Ref("TableReferenceSegment")),
            Sequence("WHERE", Ref("ExpressionSegment")),
        ),
    )


TXN_BEGIN_KEYWORDS = {"BEGIN", "START"}
TXN_END_KEYWORDS = {"END", "COMMIT", "ROLLBACK"}
