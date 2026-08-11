/*
 * SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
 * Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
 *
 * This file is part of pulse-data.
 *
 * pulse-data is dual-licensed:
 *   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
 *   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
 *     Contact operations@inventzia.com.
 */
package com.inventzia.pulse.data.datum;

import java.util.Collection;
import java.util.Optional;

/**
 * Declares a set of {@link Datum} types contributed by one package (pulse-data itself, or
 * an independent extension). A provider is pure declarative metadata plus
 * {@link DatumTypeBinding} descriptors, with no network, authentication, or gateway side
 * effects on construction.
 *
 * <p>Extension providers are discovered through {@link java.util.ServiceLoader} (a
 * {@code META-INF/services/com.inventzia.pulse.data.datum.DatumTypeProvider} file), and
 * therefore require a <b>public no-argument constructor</b>. The core provider is seeded
 * directly by {@link DatumTypeRegistry}, not discovered. Mirrors the Python
 * {@code DatumTypeProvider}.
 */
public interface DatumTypeProvider {

    /** Reverse-DNS namespace root; every contributed {@code TYPE_ID} starts with it + '.'. */
    String providerId();

    /** The SPI contract version this provider was built against (see {@link DatumTypeRegistry#SPI_VERSION}). */
    int spiVersion();

    /** The contributing distribution's version (informational; baked at build time). */
    String packageVersion();

    /** The type bindings this provider contributes. */
    Collection<DatumTypeBinding> bindings();

    /** Reserved for Phase 2 (schema-manifest fingerprinting); empty in Phase 1. */
    default Optional<String> manifest() {
        return Optional.empty();
    }
}
