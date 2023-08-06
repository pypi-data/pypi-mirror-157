# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from __future__ import annotations

import os
from glob import glob
from importlib import import_module

RULES = []

rules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "[!_]*.py"))
base_module = __name__
prefix = base_module.split(".")[-1].upper()

for module in sorted(glob(rules_path)):
    mod_name = os.path.splitext(os.path.basename(module))[0]
    code = mod_name[:4]
    rule_module = import_module(f"{base_module}.{mod_name}")
    rule_class = getattr(rule_module, "Rule")  # noqa: B009
    RULES.append(rule_class)
