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

/**
 * One contributed type: its {@code TYPE_ID}, {@code TYPE_VERSION}, and model class.
 *
 * <p>A {@link DatumTypeProvider} returns bindings rather than bare classes because
 * {@code TYPE_ID} / {@code TYPE_VERSION} are static fields, not part of the {@link Datum}
 * interface, so reading them off a {@code Class<? extends Datum>} on the hot path would
 * need reflection. The generated provider builds each binding from the class's own
 * constants ({@code CdfBar.TYPE_ID}, {@code CdfBar.TYPE_VERSION}), so nothing is duplicated.
 * Mirrors the Python {@code DatumTypeBinding}.
 *
 * @param typeId       the stable type identifier
 * @param typeVersion  the wire/schema version (positive)
 * @param datumClass   the model class
 */
public record DatumTypeBinding(String typeId, int typeVersion, Class<? extends Datum> datumClass) {
}
