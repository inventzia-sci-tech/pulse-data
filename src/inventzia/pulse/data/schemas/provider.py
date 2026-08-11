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

"""The core datum-type provider (generated): pulse-data's own Datum types."""

from inventzia.pulse.data.datum.provider import DatumTypeBinding
from inventzia.pulse.data.schemas.common.vector_value import VectorValue
from inventzia.pulse.data.schemas.marketdata.cdf_bar import CdfBar
from inventzia.pulse.data.schemas.platform.heart_beat import HeartBeat
from inventzia.pulse.data.schemas.platform.text_message import TextMessage


class CoreDatumTypeProvider:
    """pulse-data's own datum types, seeded directly into the registry."""

    def provider_id(self) -> str:
        return "com.inventzia.pulse.data"

    def spi_version(self) -> int:
        return 1

    def package_version(self) -> str:
        return "0.2.0"

    def bindings(self) -> "list[DatumTypeBinding]":
        return [
            DatumTypeBinding(VectorValue.TYPE_ID, VectorValue.TYPE_VERSION, VectorValue),
            DatumTypeBinding(CdfBar.TYPE_ID, CdfBar.TYPE_VERSION, CdfBar),
            DatumTypeBinding(HeartBeat.TYPE_ID, HeartBeat.TYPE_VERSION, HeartBeat),
            DatumTypeBinding(TextMessage.TYPE_ID, TextMessage.TYPE_VERSION, TextMessage),
        ]

    def manifest(self):
        return None  # reserved for Phase 2 (schema-manifest fingerprinting)
