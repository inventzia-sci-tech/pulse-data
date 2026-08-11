# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""The composite datum-type registry: TYPE_ID <-> model class.

Built once from the core provider (seeded directly) plus discovered extension
providers, validated, then frozen. The tagged codec resolves types through it. This is
hand-written infrastructure; the per-provider bindings are generated. Mirror of the Java
``DatumTypeRegistry``.
"""

import re
import threading
from importlib.metadata import entry_points

import pydantic

from inventzia.pulse.data.datum.provider import SPI_VERSION, DatumTypeBinding, DatumTypeProvider

_ENTRY_POINT_GROUP = "inventzia.pulse.datum_types"
_ID_RE = re.compile(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+")   # reverse-DNS-ish: dotted segments


class Registry:
    """An immutable TYPE_ID <-> class registry. Build via :func:`build_registry`."""

    __slots__ = ("_by_id", "_by_class")

    def __init__(self, by_id: dict, by_class: dict):
        self._by_id = by_id
        self._by_class = by_class

    def class_for(self, type_id: str) -> type:
        """Return the model class registered for a TYPE_ID."""
        try:
            return self._by_id[type_id]
        except KeyError:
            raise KeyError(f"Unknown TYPE_ID: {type_id!r}") from None

    def type_id_of(self, datum) -> str:
        """Return the TYPE_ID of a datum, verified against the registry.

        Encoding must not emit a tagged envelope for a class that is not the registered
        binding for its declared TYPE_ID, or a receiver could get a typeId no runtime can
        decode. Mirrors the Java ``DatumTypeRegistry.typeIdOf`` check.
        """
        cls = type(datum)
        type_id = self._by_class.get(cls)
        if type_id is None:
            raise KeyError(f"Unregistered datum type: {cls.__name__}")
        return type_id


def _fail(msg: str) -> "None":
    raise ValueError(f"invalid datum-type registry: {msg}")


def _validate_class(provider_id: str, b: DatumTypeBinding) -> None:
    cls = b.datum_class
    if cls is None:
        _fail(f"provider '{provider_id}' has a binding with no class")
    if not isinstance(cls, type) or not issubclass(cls, pydantic.BaseModel):
        _fail(f"provider '{provider_id}' type '{b.type_id}': class {cls!r} is not a pydantic BaseModel "
              "(the codec calls model_validate_json / model_dump_json)")
    for prop in ("datum_key", "datum_time"):
        if not hasattr(cls, prop):
            _fail(f"provider '{provider_id}' type '{b.type_id}': class {cls.__name__} lacks '{prop}'")
    cls_type_id = getattr(cls, "TYPE_ID", None)
    if cls_type_id != b.type_id:
        _fail(f"provider '{provider_id}': binding type_id '{b.type_id}' does not match "
              f"{cls.__name__}.TYPE_ID {cls_type_id!r} (descriptor drift)")
    tv = b.type_version
    if type(tv) is not int or tv <= 0:
        _fail(f"provider '{provider_id}' type '{b.type_id}': TYPE_VERSION must be a positive int, got {tv!r}")


def build_registry(providers) -> Registry:
    """Validate ``providers`` and build an immutable composite registry.

    ``providers`` is an ordered iterable of :class:`DatumTypeProvider` (core first). The
    validation rejects, with the offending provider/type named: null providers or bindings;
    empty or malformed provider / type IDs; blank package versions; an SPI version mismatch;
    an empty provider; a class that is not a valid pydantic datum; TYPE_VERSION that is not a
    positive int; a TYPE_ID outside ``provider_id + '.'``; a duplicate class within a provider;
    a duplicate TYPE_ID across providers; and a class bound to more than one TYPE_ID.
    """
    by_id: dict = {}
    by_class: dict = {}
    seen_provider_ids: set = set()

    for provider in providers:
        if provider is None:
            _fail("a provider is None")
        pid = provider.provider_id()
        if not pid or not pid.strip() or not _ID_RE.fullmatch(pid):
            _fail(f"provider has an empty or malformed provider_id: {pid!r}")
        if pid in seen_provider_ids:
            _fail(f"duplicate provider_id '{pid}'")
        seen_provider_ids.add(pid)
        if provider.spi_version() != SPI_VERSION:
            _fail(f"provider '{pid}' targets SPI version {provider.spi_version()}, "
                  f"this pulse-data supports {SPI_VERSION}")
        pv = provider.package_version()
        if not pv or not pv.strip():
            _fail(f"provider '{pid}' has a missing or blank package_version")

        bindings = provider.bindings()
        if bindings is None:
            _fail(f"provider '{pid}' returned no bindings collection")
        bindings = sorted(bindings, key=lambda b: (b.type_id or ""))
        if not bindings:
            _fail(f"provider '{pid}' contributes no datum types")

        provider_classes: set = set()
        for b in bindings:
            if b is None:
                _fail(f"provider '{pid}' has a None binding")
            if not b.type_id or not b.type_id.strip():
                _fail(f"provider '{pid}' has an empty or malformed type_id")
            if not b.type_id.startswith(pid + "."):
                _fail(f"provider '{pid}' type '{b.type_id}' is not under its namespace '{pid}.'")
            _validate_class(pid, b)
            if b.datum_class in provider_classes:
                _fail(f"provider '{pid}' binds class {b.datum_class.__name__} more than once")
            provider_classes.add(b.datum_class)
            if b.type_id in by_id:
                _fail(f"duplicate TYPE_ID '{b.type_id}' (provider '{pid}' conflicts with an earlier provider)")
            if b.datum_class in by_class:
                _fail(f"class {b.datum_class.__name__} is bound to more than one TYPE_ID")
            by_id[b.type_id] = b.datum_class
            by_class[b.datum_class] = b.type_id

    return Registry(by_id, by_class)


def _discover_providers() -> list:
    """Seed the core provider directly, then discover extension providers.

    Core is instantiated directly (never via discovery), so a source-tree or mis-packaged
    install cannot lose its core types and core-only parity is guaranteed. Extensions are
    loaded from the entry-point group and sorted by provider_id for determinism.
    """
    from inventzia.pulse.data.schemas.provider import CoreDatumTypeProvider

    providers = [CoreDatumTypeProvider()]
    extensions = []
    for ep in entry_points(group=_ENTRY_POINT_GROUP):
        provider_cls = ep.load()   # entry point resolves to the class, not an instance
        extensions.append(provider_cls())
    extensions.sort(key=lambda p: p.provider_id())
    providers.extend(extensions)
    return providers


_default_lock = threading.Lock()
_default_registry: "Registry | None" = None


def default_registry() -> Registry:
    """The process-wide composite registry, built once (lazily) and frozen."""
    global _default_registry
    if _default_registry is None:
        with _default_lock:
            if _default_registry is None:
                _default_registry = build_registry(_discover_providers())
    return _default_registry


def class_for(type_id: str) -> type:
    """Facade over :func:`default_registry`: TYPE_ID -> model class."""
    return default_registry().class_for(type_id)


def type_id_of(datum) -> str:
    """Facade over :func:`default_registry`: verified TYPE_ID of a datum."""
    return default_registry().type_id_of(datum)
