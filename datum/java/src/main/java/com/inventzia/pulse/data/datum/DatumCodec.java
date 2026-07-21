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

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.inventzia.pulse.data.schemas.DatumTypeRegistry;

import java.io.IOException;
import java.math.BigDecimal;

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
        // Write BigDecimal as a JSON string (not a number), so exact decimals survive
        // the cross-language boundary: Python (Pydantic) also serializes Decimal as a
        // string, and a JSON number would risk float rounding. Jackson's default
        // BigDecimal deserializer already reads strings back, so no custom reader is needed.
        SimpleModule decimalAsString = new SimpleModule().addSerializer(
                BigDecimal.class, new JsonSerializer<BigDecimal>() {
                    @Override
                    public void serialize(BigDecimal value, JsonGenerator gen, SerializerProvider sp)
                            throws IOException {
                        gen.writeString(value.toPlainString());
                    }
                });

        this.mapper = JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .addModule(decimalAsString)
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
                .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                // Serialize only the explicitly annotated record components. Without
                // this, Jackson would auto-detect the Datum accessors getDatumKey()/
                // getDatumTime() as extra "datumKey"/"datumTime" properties — bloating
                // the wire and breaking Python decode (its models are extra='forbid').
                .visibility(PropertyAccessor.GETTER, JsonAutoDetect.Visibility.NONE)
                .visibility(PropertyAccessor.IS_GETTER, JsonAutoDetect.Visibility.NONE)
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

    // ------------------------------------------------------------------
    // Self-describing (tagged) form
    //
    // The type-directed methods above need the caller to know the class.
    // The tagged form embeds the TYPE_ID in a small envelope, so a receiver
    // can recover the type from the message itself — required wherever the
    // type is not known ahead of time (the cross-language bridge, and later
    // the socket/ZMQ transport). The class is resolved through the generated
    // {@link DatumTypeRegistry}.
    // ------------------------------------------------------------------

    private static final String FIELD_TYPE_ID = "typeId";
    private static final String FIELD_PAYLOAD = "payload";

    /**
     * Serializes a datum to a self-describing envelope:
     * {@code {"typeId": "<TYPE_ID>", "payload": { ...fields... }}}.
     *
     * @param datum the datum to serialize
     * @return its tagged JSON representation
     * @throws DatumCodecException if serialization fails
     */
    public String toTaggedJson(Datum datum) {
        ObjectNode envelope = mapper.createObjectNode();
        envelope.put(FIELD_TYPE_ID, DatumTypeRegistry.typeIdOf(datum));
        envelope.set(FIELD_PAYLOAD, mapper.valueToTree(datum));
        try {
            return mapper.writeValueAsString(envelope);
        } catch (JsonProcessingException e) {
            throw new DatumCodecException(
                    "Failed to serialize tagged " + datum.getClass().getName(), e);
        }
    }

    /**
     * Deserializes a self-describing envelope produced by {@link #toTaggedJson},
     * recovering the concrete type from its {@code typeId} via the registry.
     *
     * @param json the tagged JSON to read
     * @return the deserialized datum
     * @throws DatumCodecException if the envelope is malformed or deserialization fails
     */
    public Datum fromTaggedJson(String json) {
        try {
            JsonNode envelope = mapper.readTree(json);
            JsonNode typeIdNode = envelope.get(FIELD_TYPE_ID);
            if (typeIdNode == null || !typeIdNode.isTextual()) {
                throw new DatumCodecException(
                        "Tagged JSON missing textual '" + FIELD_TYPE_ID + "': " + json);
            }
            Class<? extends Datum> type = DatumTypeRegistry.classFor(typeIdNode.asText());
            return mapper.treeToValue(envelope.get(FIELD_PAYLOAD), type);
        } catch (JsonProcessingException e) {
            throw new DatumCodecException("Failed to deserialize tagged datum from: " + json, e);
        }
    }
}
