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
 *
 * THIS FILE IS GENERATED. DO NOT EDIT MANUALLY.
 * Source: all schemas under schemas_yaml/
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas;

import com.inventzia.pulse.data.datum.DatumTypeBinding;
import com.inventzia.pulse.data.datum.DatumTypeProvider;
import com.inventzia.pulse.data.schemas.common.VectorValue;
import com.inventzia.pulse.data.schemas.marketdata.CdfBar;
import com.inventzia.pulse.data.schemas.platform.HeartBeat;
import com.inventzia.pulse.data.schemas.platform.TextMessage;
import java.util.Collection;
import java.util.List;

/**
 * The core datum-type provider (generated): pulse-data's own {@code Datum} types,
 * seeded directly into the composite {@link DatumTypeProvider} registry.
 */
public final class CoreDatumTypeProvider implements DatumTypeProvider {

    @Override public String providerId()     { return "com.inventzia.pulse.data"; }
    @Override public int    spiVersion()      { return 1; }
    @Override public String packageVersion()  { return "0.2.0"; }

    @Override
    public Collection<DatumTypeBinding> bindings() {
        return List.of(
                new DatumTypeBinding(VectorValue.TYPE_ID, VectorValue.TYPE_VERSION, VectorValue.class),
                new DatumTypeBinding(CdfBar.TYPE_ID, CdfBar.TYPE_VERSION, CdfBar.class),
                new DatumTypeBinding(HeartBeat.TYPE_ID, HeartBeat.TYPE_VERSION, HeartBeat.class),
                new DatumTypeBinding(TextMessage.TYPE_ID, TextMessage.TYPE_VERSION, TextMessage.class)
        );
    }
}
