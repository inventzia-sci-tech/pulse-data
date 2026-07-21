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
  - Lives under inventzia.pulse.data.schemas.<subpackage> (mirrors the Java
    package and the inventzia.pulse.data.datum protocol — one namespace, two
    languages)
  - Extends pydantic.BaseModel with model_config(extra='ignore') so unknown
    fields from a newer producer are tolerated (forward compatibility, matching
    the Java DatumCodec which disables FAIL_ON_UNKNOWN_PROPERTIES)
  - Declares TYPE_ID (equals the schema $id) and TYPE_VERSION as ClassVars
  - Implements datum_key and datum_time properties driven by x-datum-key /
    x-datum-time YAML annotations
  - Satisfies the inventzia.pulse.data.datum.Datum Protocol structurally

A generated ``registry.py`` (the Python mirror of the Java DatumTypeRegistry)
maps every TYPE_ID to its model class, so the codec can deserialize a tagged
envelope without being told the type.

The output tree uses PEP 420 namespace packages (no __init__.py): the
``inventzia.pulse.data`` prefix is shared with the hand-written datum protocol
in datum/python, so both source roots merge into one import namespace.

Usage (defaults are script-relative and regenerate the installable tree at
pulse-data/src/inventzia/pulse/data/schemas/, so this works from any directory):
    python generate_python.py

    # Explicit (equivalent to the defaults):
    python generate_python.py \\
        --schemas-dir  <pulse-data>/schemas/schemas_yaml \\
        --output-dir   <pulse-data>/src \\
        --base-package inventzia.pulse.data.schemas

    # Dry run:
    python generate_python.py --dry-run -v
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Script-relative defaults: input YAML lives next to this generator, output goes
# to the installable src/ tree — so `python generate_python.py` regenerates the
# canonical location from any working directory (not the removed schemas_py/).
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent                  # .../schemas/schemas-generators
_DEFAULT_SCHEMAS_DIR = _HERE.parent / "schemas_yaml"     # .../schemas/schemas_yaml
_DEFAULT_OUTPUT_DIR = _HERE.parent.parent / "src"        # .../pulse-data/src

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

_REGISTRY_HEADER = """\
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
# Source: all schemas under schemas_yaml/
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
                   base_package: str, dry_run: bool, verbose: bool) -> dict | None:
    """Generate one model. Returns metadata for the registry, or None on skip."""
    with open(schema_path, encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    title       = schema.get("title")
    description = schema.get("description", "").strip().replace("\n", " ")
    schema_id   = schema.get("$id", "")
    properties  = schema.get("properties", {})
    required    = set(schema.get("required", []))

    if not title:
        print(f"  ⚠  Skipping {schema_path.name}: no 'title' field", file=sys.stderr)
        return None

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
        return None

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

    # Derive package + output path (mirrors directory structure under base package)
    rel          = schema_path.relative_to(schemas_root)
    subpkg_parts = list(rel.parent.parts)          # e.g. ["marketdata"]
    package      = ".".join([base_package, *subpkg_parts]) if subpkg_parts else base_package
    module       = _snake(title)
    output_file  = output_root / Path(*package.split(".")) / f"{module}.py"

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
    lines.append(f'    model_config = ConfigDict(extra="ignore")')
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
    meta = {"type_id": schema_id, "package": package, "module": module, "class_name": title}

    if dry_run:
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  {schema_path.name}  →  {output_file.relative_to(output_root)}")
            print(f"{'─'*60}")
            print(source)
        else:
            print(f"  {schema_path.name}  →  {output_file.relative_to(output_root)}")
        return meta

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(source, encoding="utf-8")
    # No __init__.py: the generated tree uses PEP 420 namespace packages so it
    # merges with the datum protocol under the shared inventzia.pulse.data prefix.
    if verbose:
        print(f"  ✅  {schema_path.name}  →  {output_file.relative_to(output_root)}")
    return meta


def generate_registry(models: list[dict], output_root: Path, base_package: str,
                      dry_run: bool, verbose: bool) -> None:
    """Emit registry.py: TYPE_ID -> model class (mirror of Java DatumTypeRegistry)."""
    models = sorted(models, key=lambda m: m["class_name"])
    lines = [_REGISTRY_HEADER, ""]
    lines.append('"""Self-describing decode support: TYPE_ID -> generated model class."""')
    lines.append("")
    for m in models:
        lines.append(f'from {m["package"]}.{m["module"]} import {m["class_name"]}')
    lines.append("")
    lines.append("")
    lines.append("REGISTRY: dict[str, type] = {")
    for m in models:
        lines.append(f'    {m["class_name"]}.TYPE_ID: {m["class_name"]},')
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("def class_for(type_id: str) -> type:")
    lines.append('    """Return the model class registered for a TYPE_ID."""')
    lines.append("    try:")
    lines.append("        return REGISTRY[type_id]")
    lines.append("    except KeyError:")
    lines.append('        raise KeyError(f"Unknown TYPE_ID: {type_id!r}") from None')
    lines.append("")
    lines.append("")
    lines.append("def type_id_of(datum) -> str:")
    lines.append('    """Return the TYPE_ID of a datum instance."""')
    lines.append("    return type(datum).TYPE_ID")
    lines.append("")

    source = "\n".join(lines)
    registry_file = output_root / Path(*base_package.split(".")) / "registry.py"

    if dry_run:
        print(f"  registry  →  {registry_file.relative_to(output_root)} ({len(models)} types)")
        if verbose:
            print(source)
        return

    registry_file.parent.mkdir(parents=True, exist_ok=True)
    registry_file.write_text(source, encoding="utf-8")
    if verbose:
        print(f"  ✅  registry  →  {registry_file.relative_to(output_root)} ({len(models)} types)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--schemas-dir",  default=str(_DEFAULT_SCHEMAS_DIR))
    parser.add_argument("--output-dir",   default=str(_DEFAULT_OUTPUT_DIR),
                        help="Root of the installable tree; models go under "
                             "<output-dir>/inventzia/pulse/data/schemas/")
    parser.add_argument("--base-package", default="inventzia.pulse.data.schemas",
                        help="Base Python package for all generated models")
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
    models: list[dict] = []
    fail = 0
    for sf in schema_files:
        meta = generate_model(sf, schemas_root, output_root,
                              args.base_package, args.dry_run, args.verbose)
        if meta:
            models.append(meta)
        else:
            fail += 1

    if models:
        generate_registry(models, output_root, args.base_package, args.dry_run, args.verbose)

    print(f"\n{'✅' if fail == 0 else '⚠ '} {len(models)} generated" +
          (f", {fail} skipped/failed" if fail else ""))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
