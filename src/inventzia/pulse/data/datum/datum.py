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
Routing contract for all data types transported on the pulse-beacon bus.

Python equivalent of the Java ``Datum`` interface.  Uses structural typing
(``Protocol``) so generated Pydantic models satisfy the contract without
explicit inheritance — they simply need ``datum_key`` and ``datum_time``
properties.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Datum(Protocol):
    """
    Every generated schema class satisfies this protocol by exposing
    ``datum_key`` and ``datum_time`` properties whose implementations
    are generated from the ``x-datum-key`` and ``x-datum-time`` YAML
    annotations on the source schema.

    In Python the contract is structural: no explicit ``implements`` is
    needed.  The pulse-beacon Python infrastructure reads these properties
    by duck typing.
    """

    @property
    def datum_key(self) -> str:
        """
        The routing key for this datum instance — e.g. an instrument
        symbol, session ID, or tenant.  Never ``None``; return an empty
        string when no key applies.
        """
        ...

    @property
    def datum_time(self) -> int:
        """
        The logical time of this datum in epoch milliseconds — when the
        underlying event occurred, not when it was published or received.
        """
        ...
