# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlfluff_schema import grammar
from sqlfluff_schema.core import PostgresRule, Q


class Rule(PostgresRule):
    """
    # Adding constraints

    ## Rationale

    > Scanning a large table to verify a new foreign key or check constraint can take a long time,
    > and other updates to the table are locked out until the `ALTER TABLE ADD CONSTRAINT` command is committed.
    > The main purpose of the `NOT VALID` constraint option is to reduce the impact of adding a constraint on concurrent updates.
    > With `NOT VALID`, the `ADD CONSTRAINT` command does not scan the table and can be committed immediately.
    > After that, a `VALIDATE CONSTRAINT` command can be issued to verify that existing rows satisfy the constraint.
    > The validation step does not need to lock out concurrent updates,
    > since it knows that other transactions will be enforcing the constraint for rows that they insert or update;
    > only pre-existing rows need to be checked. Hence, validation acquires only a `SHARE UPDATE EXCLUSIVE` lock on the table being altered.
    > [...]
    > Adding a constraint using an existing index can be helpful in situations where a new constraint needs to be added
    > without blocking table updates for a long time.
    > [[ref]](https://www.postgresql.org/docs/current/sql-altertable.html)

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);
    ```

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT addr_fk FOREIGN KEY (address) REFERENCES addresses (id);
    ```

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT dist_id_unq UNIQUE (dist_id);
    ```

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT dist_id_pk PRIMARY KEY (id);
    ```

    ## Alternative

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5) NOT VALID;
    ALTER TABLE distributors VALIDATE CONSTRAINT zipchk;
    ```

    ``` postgresql
    ALTER TABLE distributors ADD CONSTRAINT addr_fk FOREIGN KEY (address) REFERENCES addresses (id) NOT VALID;
    ALTER TABLE distributors VALIDATE CONSTRAINT addr_fk;
    ```

    ``` postgresql
    CREATE UNIQUE INDEX CONCURRENTLY dist_unq_idx ON distributors (dist_id);
    ALTER TABLE distributors ADD CONSTRAINT dist_id_unq UNIQUE USING INDEX dist_unq_idx;
    ```

    ``` postgresql
    CREATE UNIQUE INDEX CONCURRENTLY dist_pk_idx ON distributors (id);
    ALTER TABLE distributors ADD CONSTRAINT dist_id_pk PRIMARY KEY USING INDEX dist_pk_idx;
    ```
    """

    groups = ("all", "migrations", "ddl")
    lints = {
        Q(grammar.AlterTableConstraint)
        & ~Q(grammar.AlterTableInvalidConstraint): "Adding constraints without `NOT VALID` or `USING INDEX` is not allowed."
    }
