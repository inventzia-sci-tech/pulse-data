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
# Source: schemas_yaml/platform/heartbeat.yaml
# Regenerate: python schemas/schemas-generators/generate_python.py

from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import ClassVar, Optional


class HeartBeat(BaseModel):
    """
    Periodic platform heartbeat produced by HeartBeatGateway. Actors subscribe to a heartbeat Topic to implement periodic behaviour (analytics windows, timeout checks) that fires at regular simulation-time intervals regardless of whether domain events arrive in that interval.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    TYPE_ID:      ClassVar[str] = "com.inventzia.pulse.data.schemas.platform.HeartBeat"
    TYPE_VERSION: ClassVar[int] = 1

    beat_key: str = Field(alias="beatKey")
    """Heartbeat identifier. Typically a fixed label (e.g. "PERIODIC") or a group key when multiple independent heartbeat streams are needed"""
    beat_time: int = Field(alias="beatTime")
    """Scheduled beat time in epoch milliseconds"""

    # -- Datum protocol ---------------------------------------------------

    @property
    def datum_key(self) -> str:
        return self.beat_key

    @property
    def datum_time(self) -> int:
        return self.beat_time
