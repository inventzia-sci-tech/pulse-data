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
Generate immutable Java record classes from YAML schemas.

Each generated class:
  - Lives under com.inventzia.pulse.data.schemas.<subpackage>
  - Implements com.inventzia.pulse.data.datum.Datum
  - Declares TYPE_ID (equals the schema $id) and TYPE_VERSION
  - Provides getDatumKey() and getDatumTime() driven by x-datum-key /
    x-datum-time YAML annotations

Usage:
    python generate_java.py \\
        --schemas-dir ../schemas_yaml \\
        --output-dir  ../schemas_java \\
        --base-package com.inventzia.pulse.data.schemas

    # Dry run (print without writing):
    python generate_java.py --schemas-dir ../schemas_yaml --dry-run -v
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
/*
 * SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
 * Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
 *
 * This file is part of pulse-data.
 *
 * pulse-data is dual-licensed:
 *   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
 *   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
 *     Contact operations@inventzia.com.
 *
 * THIS FILE IS GENERATED. DO NOT EDIT MANUALLY.
 * Source: {schema_rel}
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */"""

# ---------------------------------------------------------------------------
# Type mapping: (json-type, format) -> (java-type, import or None, boxed-type)
# boxed-type is used for optional (nullable) fields
# ---------------------------------------------------------------------------

_TYPES = {
    ("string",  None):        ("String",     None,                        "String"),
    ("string",  "date-time"): ("Instant",    "java.time.Instant",         "Instant"),
    ("string",  "date"):      ("LocalDate",  "java.time.LocalDate",       "LocalDate"),
    ("integer", None):        ("long",       None,                        "Long"),
    ("integer", "int64"):     ("long",       None,                        "Long"),
    ("integer", "int32"):     ("int",        None,                        "Integer"),
    ("number",  None):        ("double",     None,                        "Double"),
    ("number",  "decimal"):   ("BigDecimal", "java.math.BigDecimal",      "BigDecimal"),
    ("boolean", None):        ("boolean",    None,                        "Boolean"),
}


def _java_type(prop: dict, required: bool) -> tuple[str, list[str]]:
    """Return (java-type-string, [imports]) for a property."""
    t   = prop.get("type", "string")
    fmt = prop.get("format")
    if t == "array":
        item = prop.get("items", {})
        _, iimp, iboxed = _TYPES.get((item.get("type", "string"), item.get("format")),
                                     _TYPES.get((item.get("type", "string"), None), ("String", None, "String")))
        # A List<boxed-element>; the List itself is nullable when the field is optional.
        return f"List<{iboxed}>", ["java.util.List"] + ([iimp] if iimp else [])
    primitive, imp, boxed = _TYPES.get((t, fmt), _TYPES.get((t, None), ("String", None, "String")))
    java_t = primitive if required else boxed   # nullable: boxed type (Jackson handles null via NON_NULL)
    return java_t, ([imp] if imp else [])


def _camel(name: str) -> str:
    """snake_case or kebab-case -> camelCase Java identifier."""
    parts = re.split(r"[_\-]", name)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def generate_record(schema_path: Path, schemas_root: Path, output_root: Path,
                    base_package: str, dry_run: bool, verbose: bool) -> dict | None:
    """Generate one record. Returns metadata for the registry, or None on skip."""
    with open(schema_path, encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    title       = schema.get("title")
    description = schema.get("description", "").strip()
    schema_id   = schema.get("$id", "")
    properties  = schema.get("properties", {})
    required    = set(schema.get("required", []))

    if not title:
        print(f"  ⚠  Skipping {schema_path.name}: no 'title' field", file=sys.stderr)
        return None

    # Derive sub-package from path relative to schemas root
    rel = schema_path.relative_to(schemas_root)
    subpkg_parts = list(rel.parent.parts)          # e.g. ["marketdata"]
    subpackage   = ".".join(subpkg_parts) if subpkg_parts else ""
    package      = f"{base_package}.{subpackage}" if subpackage else base_package
    class_name   = title                           # e.g. "CdfBar", "HeartBeat"

    # Collect datum routing fields
    datum_key_field  = None
    datum_time_field = None
    for fname, fprop in properties.items():
        if fprop.get("x-datum-key"):
            datum_key_field = _camel(fname)
        if fprop.get("x-datum-time"):
            datum_time_field = _camel(fname)

    if not datum_key_field or not datum_time_field:
        print(f"  ⚠  {schema_path.name}: missing x-datum-key or x-datum-time annotation",
              file=sys.stderr)
        return None

    # Parallel-array constraints (x-parallel-to): enforced in the compact constructor.
    parallels = [(_camel(fn), _camel(fp["x-parallel-to"]))
                 for fn, fp in properties.items() if fp.get("x-parallel-to")]

    # Build record components and collect imports
    components = []
    imports    = set()
    imports.add("com.fasterxml.jackson.annotation.JsonInclude")
    imports.add("com.fasterxml.jackson.annotation.JsonProperty")
    imports.add("com.inventzia.pulse.data.datum.Datum")

    for fname, fprop in properties.items():
        is_required = fname in required
        java_t, imps = _java_type(fprop, is_required)
        imports.update(imps)
        java_name = _camel(fname)
        is_array  = fprop.get("type") == "array"
        desc      = fprop.get("description", "").strip().rstrip(".")
        components.append((fname, java_name, java_t, is_array, is_required, desc))

    # Nullable annotation import when any optional field present
    optional_fields = [c for c in components if c[0] not in required]
    if optional_fields:
        imports.add("org.jspecify.annotations.Nullable")

    # Immutability + validity, enforced in a compact constructor: null-check required
    # object fields, take unmodifiable defensive copies of List fields (so neither the
    # caller's original list nor the accessor's return can mutate the record), then the
    # parallel-length constraints. Primitive (long/int/double/boolean) and already-
    # immutable (String/BigDecimal/…) fields need nothing.
    _PRIMITIVES = {"long", "int", "double", "boolean"}
    ctor_body: list[str] = []
    for fname, java_name, java_t, is_array, is_req, desc in components:
        if is_array and is_req:
            ctor_body.append(f"        {java_name} = List.copyOf({java_name});")
        elif is_array:
            ctor_body.append(f"        {java_name} = {java_name} == null ? null : List.copyOf({java_name});")
        elif is_req and java_t not in _PRIMITIVES:
            ctor_body.append(f'        {java_name} = Objects.requireNonNull({java_name}, "{java_name}");')
    for pf, pt in parallels:
        ctor_body.append(f"        if ({pf} != null && {pt} != null && {pf}.size() != {pt}.size()) {{")
        ctor_body.append(f"            throw new IllegalArgumentException(")
        ctor_body.append(f'                "{pf} length (" + {pf}.size() + ") must equal {pt} length (" + {pt}.size() + ")");')
        ctor_body.append(f"        }}")
    if any("Objects.requireNonNull" in ln for ln in ctor_body):
        imports.add("java.util.Objects")

    # Output path
    pkg_path    = Path(*package.split("."))
    output_file = output_root / pkg_path / f"{class_name}.java"

    # ---------------------------------------------------------------------------
    # Render
    # ---------------------------------------------------------------------------
    schema_rel = str(schema_path.relative_to(schemas_root.parent))
    lines = [_HEADER.format(schema_rel=schema_rel), ""]
    lines.append(f"package {package};")
    lines.append("")

    for imp in sorted(imports):
        lines.append(f"import {imp};")
    lines.append("")

    # Javadoc
    if description:
        desc_lines = description.splitlines()
        lines.append("/**")
        for dl in desc_lines:
            lines.append(f" * {dl}")
        lines.append(f" *")
        lines.append(f" * <p>Type ID: {{@value #TYPE_ID}}")
        lines.append(" */")

    lines.append("@JsonInclude(JsonInclude.Include.NON_NULL)")
    lines.append(f"public record {class_name}(")

    # Record components
    comp_lines = []
    for fname, java_name, java_t, is_array, is_req, desc in components:
        nullable_ann = "@Nullable " if fname not in required else ""
        comp_lines.append(
            f"    @JsonProperty(\"{fname}\") {nullable_ann}{java_t} {java_name}"
        )
    lines.append(",\n".join(comp_lines))
    lines.append(f") implements Datum {{")
    lines.append("")
    if ctor_body:
        lines.append(f"    public {class_name} {{")
        lines.extend(ctor_body)
        lines.append(f"    }}")
        lines.append("")
    lines.append(f"    public static final String TYPE_ID      = \"{schema_id}\";")
    lines.append(f"    public static final int    TYPE_VERSION = 1;")
    lines.append("")
    lines.append(f"    @Override public String getDatumKey()  {{ return {datum_key_field}; }}")
    lines.append(f"    @Override public long   getDatumTime() {{ return {datum_time_field}; }}")
    lines.append("}")
    lines.append("")

    source = "\n".join(lines)
    meta = {"type_id": schema_id, "package": package, "class_name": class_name}

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
    if verbose:
        print(f"  ✅  {schema_path.name}  →  {output_file.relative_to(output_root)}")
    return meta


def generate_registry(models: list[dict], output_root: Path, base_package: str,
                      dry_run: bool, verbose: bool) -> None:
    """Emit DatumTypeRegistry.java: TYPE_ID <-> Class, code-generated and exhaustive."""
    models = sorted(models, key=lambda m: m["class_name"])
    registry_pkg = base_package          # com.inventzia.pulse.data.schemas
    schema_rel = "all schemas under schemas_yaml/"

    lines = [_HEADER.format(schema_rel=schema_rel), ""]
    lines.append(f"package {registry_pkg};")
    lines.append("")
    lines.append("import com.inventzia.pulse.data.datum.Datum;")
    for m in models:
        lines.append(f'import {m["package"]}.{m["class_name"]};')
    lines.append("import java.util.Map;")
    lines.append("import java.util.Set;")
    lines.append("")
    lines.append("/**")
    lines.append(" * Generated registry mapping each {@code TYPE_ID} to its generated")
    lines.append(" * {@link Datum} class (and back), so {@code DatumCodec} can deserialize a")
    lines.append(" * self-describing tagged envelope without being told the type in advance.")
    lines.append(" *")
    lines.append(" * <p>The modern form of the old hand-maintained datum-id factory: generated")
    lines.append(" * from the same YAML as the records, so it stays exhaustive automatically.")
    lines.append(" */")
    lines.append("public final class DatumTypeRegistry {")
    lines.append("")
    lines.append("    private DatumTypeRegistry() {")
    lines.append("    }")
    lines.append("")
    lines.append("    private static final Map<String, Class<? extends Datum>> BY_ID = Map.ofEntries(")
    by_id = [f'            Map.entry({m["class_name"]}.TYPE_ID, {m["class_name"]}.class)' for m in models]
    lines.append(",\n".join(by_id))
    lines.append("    );")
    lines.append("")
    lines.append("    private static final Map<Class<? extends Datum>, String> BY_CLASS = Map.ofEntries(")
    by_class = [f'            Map.entry({m["class_name"]}.class, {m["class_name"]}.TYPE_ID)' for m in models]
    lines.append(",\n".join(by_class))
    lines.append("    );")
    lines.append("")
    lines.append("    /** @return the generated class registered for a {@code TYPE_ID}. */")
    lines.append("    public static Class<? extends Datum> classFor(String typeId) {")
    lines.append("        Class<? extends Datum> type = BY_ID.get(typeId);")
    lines.append("        if (type == null) {")
    lines.append('            throw new IllegalArgumentException("Unknown TYPE_ID: " + typeId);')
    lines.append("        }")
    lines.append("        return type;")
    lines.append("    }")
    lines.append("")
    lines.append("    /** @return the {@code TYPE_ID} for a datum instance. */")
    lines.append("    public static String typeIdOf(Datum datum) {")
    lines.append("        String typeId = BY_CLASS.get(datum.getClass());")
    lines.append("        if (typeId == null) {")
    lines.append('            throw new IllegalArgumentException(')
    lines.append('                    "Unregistered datum type: " + datum.getClass().getName());')
    lines.append("        }")
    lines.append("        return typeId;")
    lines.append("    }")
    lines.append("")
    lines.append("    /** @return all registered TYPE_IDs. */")
    lines.append("    public static Set<String> typeIds() {")
    lines.append("        return BY_ID.keySet();")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    source = "\n".join(lines)
    registry_file = output_root / Path(*registry_pkg.split(".")) / "DatumTypeRegistry.java"

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
    parser.add_argument("--schemas-dir",  default="../schemas_yaml",
                        help="Root directory of YAML schemas")
    parser.add_argument("--output-dir",   default="../schemas_java",
                        help="Root output directory for generated Java files")
    parser.add_argument("--base-package", default="com.inventzia.pulse.data.schemas",
                        help="Base Java package for all generated classes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print generated output without writing files")
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

    print(f"{'[dry-run] ' if args.dry_run else ''}Generating Java records from {schemas_root}")
    models: list[dict] = []
    fail = 0
    for sf in schema_files:
        meta = generate_record(sf, schemas_root, output_root,
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
