# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""Shared schema-manifest canonicalization for the datum-type SPI (Phase 2).

Imported by *both* generators so a single implementation computes the manifest and both
bake identical bytes into their generated provider. The runtime never reconstructs a wire
schema; it only combines and validates these pre-baked manifests.

The normalizer is a closed whitelist: it fails on any wire-relevant construct it does not
support, rather than omitting it from the fingerprint (which could give equal fingerprints
to incompatible types).
"""

import hashlib
import json

MANIFEST_FORMAT = "pdm1"

# Keywords the normalizer understands. Anything wire-relevant outside these fails generation.
_TOP_KEYWORDS = {"$schema", "$id", "title", "description", "type", "properties", "required",
                 "additionalProperties", "x-version"}
_PROP_KEYWORDS = {"type", "description", "format", "items",
                  "x-datum-key", "x-datum-time", "x-parallel-to"}
_ITEM_KEYWORDS = {"type", "format"}
_PROP_TYPES = {"string", "integer", "number", "boolean", "array"}
_ITEM_TYPES = {"string", "integer", "number", "boolean"}          # no nested objects/arrays yet
_FORMATS = {None, "int64", "int32", "decimal", "date", "date-time"}


class UnsupportedSchema(Exception):
    """A schema uses a wire-relevant construct the manifest normalizer does not support."""


def _fail(msg: str):
    raise UnsupportedSchema(msg)


def _normalize_items(name: str, items: dict) -> dict:
    for k in items:
        if k not in _ITEM_KEYWORDS:
            _fail(f"property '{name}' items: unsupported keyword '{k}'")
    t = items.get("type", "string")
    if t not in _ITEM_TYPES:
        _fail(f"property '{name}' items: unsupported element type '{t}' (nesting not yet supported)")
    fmt = items.get("format")
    if fmt not in _FORMATS:
        _fail(f"property '{name}' items: unsupported format '{fmt}'")
    e = {"type": t}
    if fmt is not None:
        e["format"] = fmt
    return e


def _normalize_prop(name: str, prop: dict, required: set) -> dict:
    for k in prop:
        if k not in _PROP_KEYWORDS:
            _fail(f"property '{name}': unsupported keyword '{k}' "
                  "(enum/const/default/constraints not yet supported)")
    t = prop.get("type", "string")
    if t not in _PROP_TYPES:
        _fail(f"property '{name}': unsupported type '{t}'")
    fmt = prop.get("format")
    if fmt not in _FORMATS:
        _fail(f"property '{name}': unsupported format '{fmt}'")
    # required (presence) and nullable (JSON null valid) are represented separately. Pulse's
    # generator maps every optional field to a nullable model field, so today nullable is
    # (name not in required); this is generator behaviour, not JSON Schema semantics.
    norm = {"type": t, "nullable": name not in required}
    if fmt is not None:
        norm["format"] = fmt
    if t == "array":
        items = prop.get("items")
        if not isinstance(items, dict):
            _fail(f"property '{name}': array requires an items object (tuple arrays unsupported)")
        norm["items"] = _normalize_items(name, items)
    if "x-parallel-to" in prop:
        norm["parallelTo"] = prop["x-parallel-to"]
    return norm


def normalize_type(schema: dict) -> dict:
    """Normalize a schema to its wire-validation surface, failing on unsupported constructs."""
    for k in schema:
        if k not in _TOP_KEYWORDS:
            _fail(f"unsupported top-level keyword '{k}'")
    if schema.get("type") != "object":
        _fail("top-level 'type' must be 'object'")
    ap = schema.get("additionalProperties", False)
    if ap is not False:
        _fail("only 'additionalProperties: false' is supported")

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    key_field = time_field = None
    norm_props = {}
    for name, prop in properties.items():
        if prop.get("x-datum-key"):
            key_field = name
        if prop.get("x-datum-time"):
            time_field = name
        norm_props[name] = _normalize_prop(name, prop, required)

    # additionalProperties, title, description are excluded: Pulse ignores unknown fields on
    # decode regardless, and titles/descriptions are not on the wire.
    return {
        "id": schema.get("$id", ""),
        "version": int(schema.get("x-version", 1)),
        "key": key_field,
        "time": time_field,
        "required": sorted(required),
        "properties": norm_props,
    }


def type_fingerprint(schema: dict) -> str:
    """SHA-256 (hex, over UTF-8) of the canonical JSON of the normalized schema."""
    canonical = json.dumps(normalize_type(schema), sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def provider_manifest(provider_id: str, entries) -> str:
    """Assemble a provider manifest string from ``(type_id, type_version, fingerprint)`` entries.

    Format: ``pdm1|<provider_id>|<TYPE_ID>:<TYPE_VERSION>:<sha256hex>;...`` with entries sorted
    by TYPE_ID. Escaping-free by construction (all fields are dotted alphanumerics / digits /
    lowercase hex), so it bakes directly as a string literal in both languages.
    """
    parts = [f"{tid}:{ver}:{fp}" for (tid, ver, fp) in sorted(entries, key=lambda e: e[0])]
    return f"{MANIFEST_FORMAT}|{provider_id}|" + ";".join(parts)
