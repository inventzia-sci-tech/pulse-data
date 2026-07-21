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
# Source: schemas_yaml/common/vector_value.yaml
# Regenerate: python schemas/schemas-generators/generate_python.py

from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import ClassVar, Optional


class VectorValue(BaseModel):
    """
    A generic timestamped vector of scalar observations, optionally labelled. A scalar value is simply the length-1 case. Suited to indicators that emit M components per timestamp (e.g. MACD -> [macd, signal, histogram]).
    """

    model_config = ConfigDict(extra="ignore")

    TYPE_ID:      ClassVar[str] = "com.inventzia.pulse.data.schemas.common.VectorValue"
    TYPE_VERSION: ClassVar[int] = 1

    key: str
    """The series or observation-source identifier"""
    time: int
    """Epoch milliseconds of the observation"""
    values: list[Decimal]
    """The M scalar observations (length 1 for a scalar value)"""

    value_ids: Optional[list[str]] = Field(None, alias="valueIds")
    """Optional labels, parallel to values (positional if absent)"""

    @model_validator(mode="after")
    def _check_parallel_lengths(self):
        if self.value_ids is not None and len(self.value_ids) != len(self.values):
            raise ValueError(
                f"value_ids length ({len(self.value_ids)}) must equal values length ({len(self.values)})")
        return self

    # -- Datum protocol ---------------------------------------------------

    @property
    def datum_key(self) -> str:
        return self.key

    @property
    def datum_time(self) -> int:
        return self.time
