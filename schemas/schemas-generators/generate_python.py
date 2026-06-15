#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""
Generate Pydantic v2 model classes from YAML schemas.

Each generated class:
  - Extends pydantic.BaseModel with model_config(extra='forbid')
  - Declares TYPE_ID (equals the schema $id) and TYPE_VERSION as ClassVars
  - Implements datum_key and datum_time properties driven by x-datum-key /
    x-datum-time YAML annotations
  - Satisfies the inventzia.pulse.data.datum.Datum Protocol structurally

Usage:
    python generate_python.py \\
        --schemas-dir ../schemas_yaml \\
        --output-dir  ../schemas_py

    # Dry run:
    python generate_python.py --schemas-dir ../schemas_yaml --dry-run -v
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# License / generation header
# ---------------------------------------------------------------------------

_HEADER = """\
# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
#
# THIS FILE IS GENERATED. DO NOT EDIT MANUALLY.
# Source: {schema_rel}
# Regenerate: python schemas/schemas-generators/generate_python.py"""

# ---------------------------------------------------------------------------
# Type mapping: (json-type, format) -> (python-type, import-tuple-or-None)
# ---------------------------------------------------------------------------

_TYPES = {
    ("string",  None):        ("str",           None),
    ("string",  "date-time"): ("AwareDatetime", ("pydantic", "AwareDatetime")),
    ("string",  "date"):      ("date",          ("datetime", "date")),
    ("integer", None):        ("int",           None),
    ("integer", "int64"):     ("int",           None),
    ("integer", "int32"):     ("int",           None),
    ("number",  None):        ("float",         None),
    ("number",  "decimal"):   ("Decimal",       ("decimal", "Decimal")),
    ("boolean", None):        ("bool",          None),
}


def _py_type(prop: dict, required: bool) -> tuple[str, tuple | None]:
    t   = prop.get("type", "string")
    fmt = prop.get("format")
    py_t, imp = _TYPES.get((t, fmt), _TYPES.get((t, None), ("str", None)))
    if not required:
        return f"Optional[{py_t}]", imp
    return py_t, imp


def _snake(name: str) -> str:
    """camelCase or mixed -> snake_case Python identifier."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def generate_model(schema_path: Path, schemas_root: Path, output_root: Path,
                   dry_run: bool, verbose: bool) -> bool:
    with open(schema_path, encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    title       = schema.get("title")
    description = schema.get("description", "").strip().replace("\n", " ")
    schema_id   = schema.get("$id", "")
    properties  = schema.get("properties", {})
    required    = set(schema.get("required", []))

    if not title:
        print(f"  ⚠  Skipping {schema_path.name}: no 'title' field", file=sys.stderr)
        return False

    datum_key_field  = None   # python field name for routing key
    datum_time_field = None   # python field name for routing time

    for fname, fprop in properties.items():
        py_fname = _snake(fname)
        if fprop.get("x-datum-key"):
            datum_key_field = py_fname
        if fprop.get("x-datum-time"):
            datum_time_field = py_fname

    if not datum_key_field or not datum_time_field:
        print(f"  ⚠  {schema_path.name}: missing x-datum-key or x-datum-time", file=sys.stderr)
        return False

    # Collect imports
    imports_from: dict[str, set[str]] = {}
    imports_from.setdefault("__future__", set()).add("annotations")
    imports_from.setdefault("typing", set()).update(["ClassVar", "Optional"])
    imports_from.setdefault("pydantic", set()).update(["BaseModel", "ConfigDict"])

    # Check whether any field needs an alias (json name differs from python name)
    needs_field = any(_snake(fn) != fn for fn in properties)
    if needs_field:
        imports_from["pydantic"].add("Field")

    fields = []
    for fname, fprop in properties.items():
        is_required = fname in required
        py_fname = _snake(fname)
        py_t, imp = _py_type(fprop, is_required)
        if imp:
            mod, sym = imp
            imports_from.setdefault(mod, set()).add(sym)
        desc = fprop.get("description", "").strip().rstrip(".")
        fields.append((fname, py_fname, py_t, is_required, desc))

    # Determine output path (mirrors directory structure of schema)
    rel         = schema_path.relative_to(schemas_root)
    subdir      = rel.parent
    output_file = output_root / subdir / f"{_snake(title)}.py"

    # ---------------------------------------------------------------------------
    # Render
    # ---------------------------------------------------------------------------
    schema_rel = str(schema_path.relative_to(schemas_root.parent))
    lines = [_HEADER.format(schema_rel=schema_rel), ""]

    for mod in sorted(imports_from):
        syms = sorted(imports_from[mod])
        lines.append(f"from {mod} import {', '.join(syms)}")
    lines.append("")
    lines.append("")

    lines.append(f'class {title}(BaseModel):')
    if description:
        lines.append(f'    """')
        lines.append(f'    {description}')
        lines.append(f'    """')
    lines.append(f'')
    lines.append(f'    model_config = ConfigDict(extra="forbid")')
    lines.append(f'')
    lines.append(f'    TYPE_ID:      ClassVar[str] = "{schema_id}"')
    lines.append(f'    TYPE_VERSION: ClassVar[int] = 1')
    lines.append(f'')

    # Required fields first, then optional
    req_fields = [(fn, pfn, pt, d) for fn, pfn, pt, req, d in fields if req]
    opt_fields = [(fn, pfn, pt, d) for fn, pfn, pt, req, d in fields if not req]

    for orig_name, py_name, py_t, desc in req_fields:
        if orig_name != py_name:
            lines.append(f'    {py_name}: {py_t} = Field(alias="{orig_name}")')
        else:
            lines.append(f'    {py_name}: {py_t}')
        if desc:
            lines.append(f'    """{desc}"""')

    if opt_fields:
        lines.append(f'')
        for orig_name, py_name, py_t, desc in opt_fields:
            if orig_name != py_name:
                lines.append(f'    {py_name}: {py_t} = Field(None, alias="{orig_name}")')
            else:
                lines.append(f'    {py_name}: {py_t} = None')
            if desc:
                lines.append(f'    """{desc}"""')

    lines.append(f'')
    lines.append(f'    # -- Datum protocol ---------------------------------------------------')
    lines.append(f'')
    lines.append(f'    @property')
    lines.append(f'    def datum_key(self) -> str:')
    lines.append(f'        return self.{datum_key_field}')
    lines.append(f'')
    lines.append(f'    @property')
    lines.append(f'    def datum_time(self) -> int:')
    lines.append(f'        return self.{datum_time_field}')
    lines.append(f'')

    source = "\n".join(lines)

    if dry_run:
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  {schema_path.name}  →  {output_file.relative_to(output_root)}")
            print(f"{'─'*60}")
            print(source)
        else:
            print(f"  {schema_path.name}  →  {output_file.relative_to(output_root)}")
        return True

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(source, encoding="utf-8")

    # Ensure __init__.py exists for each package directory
    pkg_dir = output_file.parent
    while pkg_dir != output_root:
        init = pkg_dir / "__init__.py"
        if not init.exists():
            init.write_text("# generated\n", encoding="utf-8")
        pkg_dir = pkg_dir.parent

    if verbose:
        print(f"  ✅  {schema_path.name}  →  {output_file.relative_to(output_root)}")
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--schemas-dir", default="../schemas_yaml")
    parser.add_argument("--output-dir",  default="../schemas_py")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    schemas_root = Path(args.schemas_dir).resolve()
    output_root  = Path(args.output_dir).resolve()

    if not schemas_root.exists():
        print(f"❌  schemas dir not found: {schemas_root}", file=sys.stderr)
        return 1

    schema_files = sorted(schemas_root.rglob("*.yaml"))
    if not schema_files:
        print(f"⚠   No YAML files found in {schemas_root}")
        return 0

    print(f"{'[dry-run] ' if args.dry_run else ''}Generating Python models from {schemas_root}")
    ok = fail = 0
    for sf in schema_files:
        if generate_model(sf, schemas_root, output_root, args.dry_run, args.verbose):
            ok += 1
        else:
            fail += 1

    print(f"\n{'✅' if fail == 0 else '⚠ '} {ok} generated" +
          (f", {fail} skipped/failed" if fail else ""))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
