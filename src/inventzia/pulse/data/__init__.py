# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""pulse-data: the Datum routing contract and generated event schemas.

See the :mod:`inventzia.pulse.data.datum` subpackage for the ``Datum`` protocol
and JSON codecs, and ``inventzia.pulse.data.schemas`` for the generated models.

``inventzia`` and ``inventzia.pulse`` are deliberately PEP 420 namespace packages
(no ``__init__.py``) so pulse-data and pulse-beacon can share the
``inventzia.pulse.*`` prefix and install side by side; from here inward the
hand-written packages are regular packages with deliberate exports.
"""
