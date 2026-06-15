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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

/**
 * The canonical JSON serializer for pulse-data {@link Datum} types.
 *
 * <p>Serialization is a first-class concern of the data layer: pulse-data owns
 * the schemas and their generated classes, so it also owns how they are written
 * to and read from the wire. Consumers (gateways, transports) use this codec and
 * never touch a JSON library directly — the underlying engine (Jackson) is an
 * implementation detail, configured here once for every field type the generated
 * schemas use:
 * <ul>
 *   <li>{@code java.time} types ({@link java.time.Instant},
 *       {@link java.time.LocalDate}) via the JSR-310 module, written as ISO-8601
 *       strings rather than numeric timestamps;</li>
 *   <li>{@link java.math.BigDecimal} for exact decimal prices (Jackson native);</li>
 *   <li>unknown properties ignored on read, so a newer producer can add fields
 *       without breaking an older consumer.</li>
 * </ul>
 *
 * <p>Use the shared {@link #instance()}: the configured mapper is immutable and
 * thread-safe, and building one is comparatively costly, so a single instance is
 * shared process-wide.
 */
public final class DatumCodec {

    private static final DatumCodec INSTANCE = new DatumCodec();

    /** @return the process-wide shared codec. */
    public static DatumCodec instance() {
        return INSTANCE;
    }

    private final JsonMapper mapper;

    private DatumCodec() {
        this.mapper = JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
                .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                .build();
    }

    /**
     * Serializes a datum to a single-line JSON string.
     *
     * @param datum the datum to serialize
     * @return its JSON representation
     * @throws DatumCodecException if serialization fails
     */
    public String toJson(Datum datum) {
        try {
            return mapper.writeValueAsString(datum);
        } catch (JsonProcessingException e) {
            throw new DatumCodecException(
                    "Failed to serialize " + datum.getClass().getName(), e);
        }
    }

    /**
     * Deserializes a JSON string into the given datum type.
     *
     * @param json the JSON to read
     * @param type the concrete datum class to produce
     * @param <P>  the datum type
     * @return the deserialized datum
     * @throws DatumCodecException if deserialization fails
     */
    public <P extends Datum> P fromJson(String json, Class<P> type) {
        try {
            return mapper.readValue(json, type);
        } catch (JsonProcessingException e) {
            throw new DatumCodecException(
                    "Failed to deserialize " + type.getName() + " from: " + json, e);
        }
    }
}
