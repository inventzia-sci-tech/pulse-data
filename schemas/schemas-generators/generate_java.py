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
  - Declares TYPE_ID (equals the schema $id) and TYPE_VERSION (from the schema's
    optional x-version, default 1; bump when the wire shape changes)
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

import manifest as _manifest
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
    type_version = int(schema.get("x-version", 1))   # wire/schema version; default 1
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

    # Record components. Required fields are marked required=true so the codec's
    # FAIL_ON_MISSING_CREATOR_PROPERTIES rejects a missing field on decode — otherwise
    # a missing required primitive (e.g. a timestamp) would silently deserialize to 0,
    # which the compact constructor cannot null-check.
    comp_lines = []
    for fname, java_name, java_t, is_array, is_req, desc in components:
        nullable_ann = "@Nullable " if not is_req else ""
        json_prop = (f'@JsonProperty(value = "{fname}", required = true)' if is_req
                     else f'@JsonProperty("{fname}")')
        comp_lines.append(f"    {json_prop} {nullable_ann}{java_t} {java_name}")
    lines.append(",\n".join(comp_lines))
    lines.append(f") implements Datum {{")
    lines.append("")
    if ctor_body:
        lines.append(f"    public {class_name} {{")
        lines.extend(ctor_body)
        lines.append(f"    }}")
        lines.append("")
    lines.append(f"    public static final String TYPE_ID      = \"{schema_id}\";")
    lines.append(f"    public static final int    TYPE_VERSION = {type_version};")
    lines.append("")
    lines.append(f"    @Override public String getDatumKey()  {{ return {datum_key_field}; }}")
    lines.append(f"    @Override public long   getDatumTime() {{ return {datum_time_field}; }}")
    lines.append("}")
    lines.append("")

    source = "\n".join(lines)
    meta = {"type_id": schema_id, "package": package, "class_name": class_name,
            "type_version": type_version, "fingerprint": _manifest.type_fingerprint(schema)}

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


_PROJECT_ROOT = Path(__file__).resolve().parents[2]   # .../pulse-data
CORE_PROVIDER_ID = "com.inventzia.pulse.data"


def _project_version() -> str:
    """The pulse-data version (base, no -SNAPSHOT), read from pom.xml so the generated
    provider cannot drift from the canonical version; regeneration-drift catches divergence."""
    text = (_PROJECT_ROOT / "pom.xml").read_text(encoding="utf-8")
    m = re.search(r"<version>([^<]+)</version>", text)
    return (m.group(1) if m else "0.0.0").replace("-SNAPSHOT", "")


def generate_provider(models: list[dict], output_root: Path, base_package: str,
                      dry_run: bool, verbose: bool) -> None:
    """Emit CoreDatumTypeProvider.java: the generated core provider (SPI binding descriptors).

    The composite registry (hand-written, datum/DatumTypeRegistry) seeds this provider
    directly and discovers extension providers around it. Bindings are sorted by TYPE_ID.
    Mirror of the Python generated CoreDatumTypeProvider.
    """
    models = sorted(models, key=lambda m: m["type_id"])
    provider_pkg = base_package          # com.inventzia.pulse.data.schemas
    version = _project_version()
    schema_rel = "all schemas under schemas_yaml/"

    lines = [_HEADER.format(schema_rel=schema_rel), ""]
    lines.append(f"package {provider_pkg};")
    lines.append("")
    lines.append("import com.inventzia.pulse.data.datum.DatumTypeBinding;")
    lines.append("import com.inventzia.pulse.data.datum.DatumTypeProvider;")
    for m in models:
        lines.append(f'import {m["package"]}.{m["class_name"]};')
    lines.append("import java.util.Collection;")
    lines.append("import java.util.List;")
    lines.append("import java.util.Optional;")
    lines.append("")
    lines.append("/**")
    lines.append(" * The core datum-type provider (generated): pulse-data's own {@code Datum} types,")
    lines.append(" * seeded directly into the composite {@link DatumTypeProvider} registry.")
    lines.append(" */")
    lines.append("public final class CoreDatumTypeProvider implements DatumTypeProvider {")
    lines.append("")
    lines.append("    @Override public String providerId()     { return \"" + CORE_PROVIDER_ID + "\"; }")
    lines.append("    @Override public int    spiVersion()      { return 1; }")
    lines.append("    @Override public String packageVersion()  { return \"" + version + "\"; }")
    lines.append("")
    lines.append("    @Override")
    lines.append("    public Collection<DatumTypeBinding> bindings() {")
    lines.append("        return List.of(")
    binds = [f'                new DatumTypeBinding({m["class_name"]}.TYPE_ID, {m["class_name"]}.TYPE_VERSION, {m["class_name"]}.class)'
             for m in models]
    lines.append(",\n".join(binds))
    lines.append("        );")
    lines.append("    }")
    lines.append("")
    manifest_str = _manifest.provider_manifest(
        CORE_PROVIDER_ID, [(m["type_id"], m["type_version"], m["fingerprint"]) for m in models])
    lines.append("    @Override")
    lines.append("    public Optional<String> manifest() {")
    lines.append(f'        return Optional.of("{manifest_str}");')
    lines.append("    }")
    lines.append("}")
    lines.append("")

    source = "\n".join(lines)
    provider_file = output_root / Path(*provider_pkg.split(".")) / "CoreDatumTypeProvider.java"

    if dry_run:
        print(f"  provider  →  {provider_file.relative_to(output_root)} ({len(models)} types)")
        if verbose:
            print(source)
        return

    provider_file.parent.mkdir(parents=True, exist_ok=True)
    provider_file.write_text(source, encoding="utf-8")
    if verbose:
        print(f"  ✅  provider  →  {provider_file.relative_to(output_root)} ({len(models)} types)")


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
        generate_provider(models, output_root, args.base_package, args.dry_run, args.verbose)

    print(f"\n{'✅' if fail == 0 else '⚠ '} {len(models)} generated" +
          (f", {fail} skipped/failed" if fail else ""))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
