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
    # Adding a column with a constraint

    ## Rationale
    Adding a new column with either `PRIMARY KEY` or `UNIQUE` constraints creates an implicit `UNIQUE` index. It might take a long time
    to build this index, as it is not done concurrently.

    Adding a new column with a `REFERENCES` constraint would lock both the source and reference tables until the constraint is validated.

    ```postgresql
    ALTER TABLE distributors ADD id BIGINT PRIMARY KEY NULL
    ```

    ```postgresql
    ALTER TABLE distributors ADD name TEXT UNIQUE NULL
    ```

    ```postgresql
    ALTER TABLE distributor ADD addr_id BIGINT REFERENCES address NULL;
    ```

    ## Alternative
    ```postgresql
    -- add column
    ALTER TABLE distributors ADD COLUMN id BIGINT NULL
    -- add unique index
    CREATE UNIQUE INDEX CONCURRENTLY dist_pk_idx ON distributors (id);
    -- add primary key constraint
    ALTER TABLE distributors ADD CONSTRAINT dist_id_pk PRIMARY KEY USING INDEX dist_pk_idx;
    ```

    ```postgresql
    -- add column
    ALTER TABLE distributors ADD name TEXT NULL
    -- add unique index
    CREATE UNIQUE INDEX CONCURRENTLY dist_unq_idx ON distributors (name);
    -- add unique constraint
    ALTER TABLE distributors ADD CONSTRAINT dist_name_unique UNIQUE USING INDEX dist_unq_idx;
    ```

    ```postgresql
    -- add column
    ALTER TABLE distributor ADD addr_id BIGINT NULL;
    -- add foreign key constraint
    ALTER TABLE distributors ADD CONSTRAINT addr_fk FOREIGN KEY (address) REFERENCES addresses (id) NOT VALID;
    ALTER TABLE distributors VALIDATE CONSTRAINT addr_fk;
    -- add an index (optional)
    CREATE UNIQUE INDEX CONCURRENTLY addr_fk_idx ON distributors (addr_id);
    ```

    See [`C003_column_add_constraint`][sqlfluff_schema.ddl.C003_column_add_constraint] for more details about adding constraints.

    For non-nullable columns, check [`C005_column_alter_not_null`][sqlfluff_schema.ddl.C005_column_alter_not_null]
    """

    groups = ("all", "migrations", "ddl")
    lints = {
        (grammar.AddColumn, grammar.PrimaryKey): "Adding a new primary key column is not allowed.",
        (grammar.AddColumn, grammar.Unique): "Adding a new unique column is not allowed.",
        (grammar.AddColumn, grammar.References): "Adding a new foreign key is not allowed.",
    }
