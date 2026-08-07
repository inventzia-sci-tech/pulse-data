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
# Regenerate: python schemas/schemas-generators/generate_python.py

"""Self-describing decode support: TYPE_ID -> generated model class."""

from inventzia.pulse.data.schemas.marketdata.cdf_bar import CdfBar
from inventzia.pulse.data.schemas.platform.heart_beat import HeartBeat
from inventzia.pulse.data.schemas.platform.text_message import TextMessage
from inventzia.pulse.data.schemas.common.vector_value import VectorValue


REGISTRY: dict[str, type] = {
    CdfBar.TYPE_ID: CdfBar,
    HeartBeat.TYPE_ID: HeartBeat,
    TextMessage.TYPE_ID: TextMessage,
    VectorValue.TYPE_ID: VectorValue,
}


def class_for(type_id: str) -> type:
    """Return the model class registered for a TYPE_ID."""
    try:
        return REGISTRY[type_id]
    except KeyError:
        raise KeyError(f"Unknown TYPE_ID: {type_id!r}") from None


def type_id_of(datum) -> str:
    """Return the TYPE_ID of a datum, verified against the registry.

    Encoding must not emit a tagged envelope for a class that is not the
    registered binding for its declared TYPE_ID, or a receiver could get a
    typeId no runtime can decode. Mirrors the Java DatumTypeRegistry check.
    """
    cls = type(datum)
    type_id = getattr(cls, "TYPE_ID", None)
    if REGISTRY.get(type_id) is not cls:
        raise KeyError(
            f"Unregistered datum type: {cls.__name__} (TYPE_ID {type_id!r})")
    return type_id
