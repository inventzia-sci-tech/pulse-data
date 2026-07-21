# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""The Datum routing contract and its JSON / tagged-JSON codecs.

    from inventzia.pulse.data.datum import Datum, to_tagged_json, from_tagged_json
"""

from inventzia.pulse.data.datum.datum import Datum
from inventzia.pulse.data.datum.codec import (
    from_json,
    from_tagged_json,
    to_json,
    to_tagged_json,
)

__all__ = [
    "Datum",
    "to_json",
    "from_json",
    "to_tagged_json",
    "from_tagged_json",
]
