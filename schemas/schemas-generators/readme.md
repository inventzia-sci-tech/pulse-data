# Schema generators

Two scripts generate strongly-typed data classes from the YAML schemas in
`schemas/schemas_yaml/`. Both walk the schema tree recursively and mirror its directory
structure into their output. Run them from this directory (`schemas/schemas-generators/`)
in the `pulse-data` conda environment.

## Java — `generate_java.py`

Generates immutable Java `record` classes into `schemas/schemas_java/`.

```bash
conda run -n pulse-data python generate_java.py \
  --schemas-dir ../schemas_yaml \
  --output-dir  ../schemas_java \
  --base-package com.inventzia.pulse.data.schemas \
  -v
```

Each record implements `com.inventzia.pulse.data.datum.Datum`, declares `TYPE_ID`
(equal to the schema `$id`) and `TYPE_VERSION`, and delegates `getDatumKey()` /
`getDatumTime()` to the fields marked `x-datum-key` / `x-datum-time`.

## Python — `generate_python.py`

Generates Pydantic v2 models into `schemas/schemas_py/`.

```bash
conda run -n pulse-data python generate_python.py \
  --schemas-dir ../schemas_yaml \
  --output-dir  ../schemas_py \
  -v
```

Each model declares `TYPE_ID` / `TYPE_VERSION` as `ClassVar`s and exposes `datum_key` /
`datum_time` properties, satisfying the `inventzia.pulse.data.datum.Datum` protocol
structurally (no inheritance).

## Common options

- `--dry-run` — print what would be generated without writing files.
- `-v` / `--verbose` — list each schema processed (with `--dry-run`, prints the full source).

## Schema requirements

Every schema must declare:

- `$id` — the fully-qualified class name; becomes `TYPE_ID`.
- `title` — the class name.
- exactly one field annotated `x-datum-key: true` and one annotated `x-datum-time: true`.

A schema missing either annotation is skipped with a warning.

## After generation

Regenerate **both** languages whenever a schema changes, and commit the YAML together with the
regenerated Java and Python output.
