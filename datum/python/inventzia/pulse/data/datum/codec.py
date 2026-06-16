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
  The class is resolved through the generated
  :mod:`inventzia.pulse.data.schemas.registry` (the mirror of Java's
  ``DatumTypeRegistry``).

The tagged envelope is identical to the Java side::

    {"typeId": "<TYPE_ID>", "payload": { ...fields... }}
"""

import json
from typing import TypeVar

from inventzia.pulse.data.schemas.registry import class_for, type_id_of

_FIELD_TYPE_ID = "typeId"
_FIELD_PAYLOAD = "payload"

T = TypeVar("T")


def to_json(datum) -> str:
    """Serialise a datum to a single-line JSON string (flat, field names = wire names)."""
    return datum.model_dump_json(by_alias=True)


def from_json(json_str: str, model_class: type[T]) -> T:
    """Deserialise a JSON string into the given model class."""
    return model_class.model_validate_json(json_str)


def to_tagged_json(datum) -> str:
    """Serialise a datum to the self-describing envelope ``{"typeId", "payload"}``."""
    payload = json.loads(datum.model_dump_json(by_alias=True))
    return json.dumps({_FIELD_TYPE_ID: type_id_of(datum), _FIELD_PAYLOAD: payload})


def from_tagged_json(json_str: str):
    """Deserialise a tagged envelope, recovering the concrete type from its ``typeId``."""
    envelope = json.loads(json_str)
    type_id = envelope.get(_FIELD_TYPE_ID)
    if not isinstance(type_id, str):
        raise ValueError(f"Tagged JSON missing textual {_FIELD_TYPE_ID!r}: {json_str}")
    model_class = class_for(type_id)
    return model_class.model_validate(envelope.get(_FIELD_PAYLOAD))
