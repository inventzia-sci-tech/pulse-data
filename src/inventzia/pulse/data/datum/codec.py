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
The Python counterpart of the Java ``DatumCodec``.

pulse-data owns how a :class:`~inventzia.pulse.data.datum.datum.Datum` becomes
JSON in *both* languages, so a value produced in one is consumed verbatim in the
other. Pydantic does the field-level (de)serialisation; this module adds the two
forms the transport layer uses:

* **type-directed** — :func:`to_json` / :func:`from_json`, when the caller knows
  the concrete model class (e.g. it knows the topic's payload type);
* **self-describing (tagged)** — :func:`to_tagged_json` / :func:`from_tagged_json`,
  which embed the ``TYPE_ID`` in a small envelope so a receiver can recover the
  type from the message itself. Required wherever the type is not known ahead of
  time: the in-process cross-language bridge, and later the socket/ZMQ transport.
  The type is resolved through the composite
  :mod:`inventzia.pulse.data.datum.registry` (the mirror of Java's
  ``DatumTypeRegistry``). The tagged functions default to the process-wide registry;
  pass ``registry=`` (or use :class:`TaggedCodec`) to bind an isolated one in tests.

The tagged envelope is identical to the Java side::

    {"typeId": "<TYPE_ID>", "payload": { ...fields... }}
"""

import json
from typing import Optional, TypeVar

from inventzia.pulse.data.datum.registry import Registry, default_registry

_FIELD_TYPE_ID = "typeId"
_FIELD_PAYLOAD = "payload"

T = TypeVar("T")


def to_json(datum) -> str:
    """Serialise a datum to a single-line JSON string (flat, field names = wire names).

    ``exclude_none=True`` omits absent optional fields, matching the Java codec's
    ``@JsonInclude(NON_NULL)`` so the two languages produce identical envelopes.
    """
    return datum.model_dump_json(by_alias=True, exclude_none=True)


def from_json(json_str: str, model_class: type[T]) -> T:
    """Deserialise a JSON string into the given model class."""
    return model_class.model_validate_json(json_str)


def to_tagged_json(datum, registry: Optional[Registry] = None) -> str:
    """Serialise a datum to the self-describing envelope ``{"typeId", "payload"}``.

    ``registry`` defaults to the process-wide composite registry; pass an isolated one
    (from ``build_registry``) to encode against a custom type universe.
    """
    reg = registry if registry is not None else default_registry()
    payload = json.loads(datum.model_dump_json(by_alias=True, exclude_none=True))
    return json.dumps({_FIELD_TYPE_ID: reg.type_id_of(datum), _FIELD_PAYLOAD: payload})


def from_tagged_json(json_str: str, registry: Optional[Registry] = None):
    """Deserialise a tagged envelope, recovering the concrete type from its ``typeId``.

    ``registry`` defaults to the process-wide composite registry.
    """
    reg = registry if registry is not None else default_registry()
    envelope = json.loads(json_str)
    type_id = envelope.get(_FIELD_TYPE_ID)
    if not isinstance(type_id, str):
        raise ValueError(f"Tagged JSON missing textual {_FIELD_TYPE_ID!r}: {json_str}")
    model_class = reg.class_for(type_id)
    return model_class.model_validate(envelope.get(_FIELD_PAYLOAD))


class TaggedCodec:
    """A tagged codec bound to a specific :class:`Registry` (for tests / isolated universes)."""

    def __init__(self, registry: Registry):
        self._registry = registry

    def to_tagged_json(self, datum) -> str:
        return to_tagged_json(datum, self._registry)

    def from_tagged_json(self, json_str: str):
        return from_tagged_json(json_str, self._registry)
