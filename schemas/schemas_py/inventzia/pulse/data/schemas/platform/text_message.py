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
# Source: schemas_yaml/platform/text_message.yaml
# Regenerate: python schemas/schemas-generators/generate_python.py

from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import ClassVar, Optional


class TextMessage(BaseModel):
    """
    Generic carrier for a free-text string payload. The platform equivalent of a plain message — useful for diagnostics, echo/relay examples, and any actor or gateway that needs to move arbitrary text on a topic.
    """

    model_config = ConfigDict(extra="ignore")

    TYPE_ID:      ClassVar[str] = "com.inventzia.pulse.data.schemas.platform.TextMessage"
    TYPE_VERSION: ClassVar[int] = 1

    msg_key: str = Field(alias="msgKey")
    """Routing key for this message — e.g. a channel, source identifier, or logical stream name"""
    msg_time: int = Field(alias="msgTime")
    """Epoch milliseconds when the message was created"""
    text: str
    """The free-text payload"""

    # -- Datum protocol ---------------------------------------------------

    @property
    def datum_key(self) -> str:
        return self.msg_key

    @property
    def datum_time(self) -> int:
        return self.msg_time
