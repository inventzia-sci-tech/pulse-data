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
# Source: schemas_yaml/marketdata/cdf_bar.yaml
# Regenerate: python schemas/schemas-generators/generate_python.py

from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from typing import ClassVar, Optional


class CdfBar(BaseModel):
    """
    Common data format (CDF) market data bar.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    TYPE_ID:      ClassVar[str] = "com.inventzia.pulse.data.schemas.marketdata.CdfBar"
    TYPE_VERSION: ClassVar[int] = 1

    symb: str
    """Instrument symbol or identifier"""
    timestamp: int
    """Epoch milliseconds representing the bar open time"""
    op: Decimal
    """Open price"""
    hi: Decimal
    """High price"""
    lo: Decimal
    """Low price"""
    cl: Decimal
    """Close price"""
    vlm: Decimal
    """Volume traded during this bar"""
    datetime: AwareDatetime
    """ISO 8601 datetime of the bar open time"""
    date: date
    """Trading date for the bar"""

    vwap: Optional[Decimal] = None
    """Volume-weighted average price (optional)"""
    count: Optional[int] = None
    """Number of trades aggregated in this bar (optional)"""
    expiry: Optional[str] = None
    """Option or futures expiry (optional)"""
    strike: Optional[Decimal] = None
    """Option strike price (optional)"""
    sym_exp: Optional[str] = Field(None, alias="symExp")
    """Symbol + expiry composite identifier (optional)"""

    # -- Datum protocol ---------------------------------------------------

    @property
    def datum_key(self) -> str:
        return self.symb

    @property
    def datum_time(self) -> int:
        return self.timestamp
