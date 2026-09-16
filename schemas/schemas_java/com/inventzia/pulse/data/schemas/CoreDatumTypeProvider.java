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
import java.util.Optional;

/**
 * Datum types contributed by com.inventzia.pulse.data (generated), discovered via the SPI.
 */
public final class CoreDatumTypeProvider implements DatumTypeProvider {

    @Override public String providerId()     { return "com.inventzia.pulse.data"; }
    @Override public int    spiVersion()      { return 1; }
    @Override public String packageVersion()  { return "0.3.0"; }

    @Override
    public Collection<DatumTypeBinding> bindings() {
        return List.of(
                new DatumTypeBinding(VectorValue.TYPE_ID, VectorValue.TYPE_VERSION, VectorValue.class),
                new DatumTypeBinding(CdfBar.TYPE_ID, CdfBar.TYPE_VERSION, CdfBar.class),
                new DatumTypeBinding(HeartBeat.TYPE_ID, HeartBeat.TYPE_VERSION, HeartBeat.class),
                new DatumTypeBinding(TextMessage.TYPE_ID, TextMessage.TYPE_VERSION, TextMessage.class)
        );
    }

    @Override
    public Optional<String> manifest() {
        return Optional.of("pdm1|com.inventzia.pulse.data|com.inventzia.pulse.data.schemas.common.VectorValue:1:47a0adfbbf19dcd7614cdf985086a67531a2bc9f5d1d6c5a5a721e6ee753ba23;com.inventzia.pulse.data.schemas.marketdata.CdfBar:1:3e6e7e76fc16188671c3c7d8036490b6c78bebcfa9293998af6d286e1a0dabd8;com.inventzia.pulse.data.schemas.platform.HeartBeat:1:5e08970887ce4d3424a8228b3a8b83622ba72a50d628ea155ca390802451844c;com.inventzia.pulse.data.schemas.platform.TextMessage:1:bb0ccb451f6abf888d58d3bab5bd82fbf31feab607139de5db38644977f1383a");
    }
}
