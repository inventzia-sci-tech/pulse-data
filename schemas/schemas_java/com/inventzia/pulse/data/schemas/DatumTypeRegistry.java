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

import com.inventzia.pulse.data.datum.Datum;
import com.inventzia.pulse.data.schemas.marketdata.CdfBar;
import com.inventzia.pulse.data.schemas.platform.HeartBeat;
import com.inventzia.pulse.data.schemas.platform.TextMessage;
import java.util.Map;
import java.util.Set;

/**
 * Generated registry mapping each {@code TYPE_ID} to its generated
 * {@link Datum} class (and back), so {@code DatumCodec} can deserialize a
 * self-describing tagged envelope without being told the type in advance.
 *
 * <p>The modern form of the old hand-maintained datum-id factory: generated
 * from the same YAML as the records, so it stays exhaustive automatically.
 */
public final class DatumTypeRegistry {

    private DatumTypeRegistry() {
    }

    private static final Map<String, Class<? extends Datum>> BY_ID = Map.ofEntries(
            Map.entry(CdfBar.TYPE_ID, CdfBar.class),
            Map.entry(HeartBeat.TYPE_ID, HeartBeat.class),
            Map.entry(TextMessage.TYPE_ID, TextMessage.class)
    );

    private static final Map<Class<? extends Datum>, String> BY_CLASS = Map.ofEntries(
            Map.entry(CdfBar.class, CdfBar.TYPE_ID),
            Map.entry(HeartBeat.class, HeartBeat.TYPE_ID),
            Map.entry(TextMessage.class, TextMessage.TYPE_ID)
    );

    /** @return the generated class registered for a {@code TYPE_ID}. */
    public static Class<? extends Datum> classFor(String typeId) {
        Class<? extends Datum> type = BY_ID.get(typeId);
        if (type == null) {
            throw new IllegalArgumentException("Unknown TYPE_ID: " + typeId);
        }
        return type;
    }

    /** @return the {@code TYPE_ID} for a datum instance. */
    public static String typeIdOf(Datum datum) {
        String typeId = BY_CLASS.get(datum.getClass());
        if (typeId == null) {
            throw new IllegalArgumentException(
                    "Unregistered datum type: " + datum.getClass().getName());
        }
        return typeId;
    }

    /** @return all registered TYPE_IDs. */
    public static Set<String> typeIds() {
        return BY_ID.keySet();
    }
}
