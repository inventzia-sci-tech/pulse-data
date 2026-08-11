# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.
"""The datum-type service-provider interface (SPI).

Each package that contributes routed :class:`Datum` types (pulse-data itself, and
independent extensions such as an adapter) publishes a :class:`DatumTypeProvider`.
A provider is pure declarative metadata plus binding descriptors, discovered once and
composed into an immutable registry (see :mod:`inventzia.pulse.data.datum.registry`).
Provider construction and loading must have no network, authentication, or gateway
side effects.

Extensions register a provider through the ``inventzia.pulse.datum_types`` packaging
entry-point group, whose value is a public zero-argument provider class; the registry
instantiates it exactly once. The core provider is generated and seeded directly, not
discovered.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

#: The SPI contract version this pulse-data implements. Providers must match it exactly.
SPI_VERSION = 1


@dataclass(frozen=True)
class DatumTypeBinding:
    """One contributed type: its ``TYPE_ID``, ``TYPE_VERSION``, and model class.

    Built from the class's own constants (``Model.TYPE_ID`` / ``Model.TYPE_VERSION``),
    so nothing is duplicated. Mirrors the Java ``DatumTypeBinding`` record.
    """

    type_id: str
    type_version: int
    datum_class: type


@runtime_checkable
class DatumTypeProvider(Protocol):
    """Declares a set of :class:`Datum` types contributed by one package."""

    def provider_id(self) -> str:
        """Reverse-DNS namespace root; every contributed ``TYPE_ID`` starts with it + '.'."""
        ...

    def spi_version(self) -> int:
        """The SPI contract version this provider was built against."""
        ...

    def package_version(self) -> str:
        """The contributing distribution's version (informational; baked at build time)."""
        ...

    def bindings(self) -> "list[DatumTypeBinding]":
        """The type bindings this provider contributes."""
        ...

    def manifest(self) -> Optional[str]:
        """Reserved for Phase 2 (schema-manifest fingerprinting). ``None`` in Phase 1."""
        ...
