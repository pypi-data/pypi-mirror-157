# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from __future__ import annotations

from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.rules.base import BaseRule, LintResult


class DialectException(Exception):
    pass


class Q:
    def __init__(self, *rules):
        self.rules = {rule: True for rule in rules}

    def __and__(self, other):
        combined = Q()
        combined.rules = {
            **self.rules,
            **other.rules,
        }
        return combined

    def __invert__(self):
        combined = Q()
        combined.rules = {rule: not value for rule, value in self.rules.items()}
        return combined


class Meta(type):
    def __new__(cls, name, bases, attrs):
        if name == "Rule":
            mods = attrs["__module__"].split(".")
            prefix = mods[-2].upper()
            mod = mods[-1]
            code = mod[:4]
            name = f"Rule_{prefix}_{code}"
            attrs["__doc__"] = attrs["__doc__"].lstrip()
        return super().__new__(cls, name, bases, attrs)


class DialectRule(BaseRule, metaclass=Meta):
    allowed_dialects = []

    def _eval(self, context):
        dialect = context.dialect
        if dialect.name in self.allowed_dialects:
            method = getattr(self, f"_eval_{dialect.name}")
            return method(context)
        raise DialectException(f"Unsupported dialect `{dialect.name}`. Allowed: `{self.allowed_dialects}`")


class PostgresRule(DialectRule):
    lints = {}
    allowed_dialects = ["postgres"]

    @classmethod
    def matches(cls, *segments, target=None, dialect=None):
        with RootParseContext(dialect=dialect, recurse=True) as ctx:
            for segment in segments:
                if not segment.is_type(target.type):
                    continue
                res = target.match_grammar.match(segments=segment.segments, parse_context=ctx)
                if res:
                    return res
        return None

    def _eval_postgres_lint(self, lint, segment, dialect):
        segments = (segment,)
        if isinstance(lint, tuple):
            idx = 0
            cnt = len(lint)
            while idx < cnt:
                res = self.matches(*segments, target=lint[idx], dialect=dialect)
                if not res:
                    return False
                segments = res.unmatched_segments
                idx += 1
            return True
        else:
            if self.matches(*segments, target=lint, dialect=dialect):
                return True
        return False

    def _eval_postgres(self, context):
        """

        :type context: sqlfluff.core.rules.base.RuleContext
        """
        segment = context.segment
        dialect = context.dialect

        for lint in self.lints:
            if isinstance(lint, Q):
                found = False
                for rule, expected in lint.rules.items():
                    if found := self._eval_postgres_lint(rule, segment, dialect=dialect) == expected:
                        continue
                    else:
                        break
                if found:
                    return LintResult(anchor=segment, description=self.lints[lint])
            else:
                if self._eval_postgres_lint(lint, segment, dialect=dialect):
                    return LintResult(anchor=segment, description=self.lints[lint])
