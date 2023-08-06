# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os

from sqlfluff.core.config import ConfigLoader
from sqlfluff.core.plugin import hookimpl

from sqlfluff_schema.ddl import RULES


@hookimpl
def get_rules():
    return RULES


@hookimpl
def load_default_config():
    return ConfigLoader.get_global().load_default_config_file(
        file_dir=os.path.dirname(__file__),
        file_name="default_config.cfg",
    )


@hookimpl
def get_configs_info():
    return {
        "forbidden_tables": {"definition": "A list of tables to forbid from being altered"},
        "allowed_key_types": {"definition": "A list of types that are allowed to be used for PK/FK"},
        "force_enable": {
            "validation": [True, False],
            "definition": "Run this rule even for dialects where this rule is disabled by default",
        },
    }
