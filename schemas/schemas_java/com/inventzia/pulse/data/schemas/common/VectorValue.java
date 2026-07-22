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
 * Source: schemas_yaml/common/vector_value.yaml
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas.common;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.inventzia.pulse.data.datum.Datum;
import java.math.BigDecimal;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * A generic timestamped vector of scalar observations, optionally labelled. A scalar value is simply the length-1 case. Suited to indicators that emit M components per timestamp (e.g. MACD -> [macd, signal, histogram]).
 *
 * <p>Type ID: {@value #TYPE_ID}
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record VectorValue(
    @JsonProperty(value = "key", required = true) String key,
    @JsonProperty(value = "time", required = true) long time,
    @JsonProperty(value = "values", required = true) List<BigDecimal> values,
    @JsonProperty("valueIds") @Nullable List<String> valueIds
) implements Datum {

    public VectorValue {
        key = Objects.requireNonNull(key, "key");
        values = List.copyOf(values);
        valueIds = valueIds == null ? null : List.copyOf(valueIds);
        if (valueIds != null && values != null && valueIds.size() != values.size()) {
            throw new IllegalArgumentException(
                "valueIds length (" + valueIds.size() + ") must equal values length (" + values.size() + ")");
        }
    }

    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.common.VectorValue";
    public static final int    TYPE_VERSION = 1;

    @Override public String getDatumKey()  { return key; }
    @Override public long   getDatumTime() { return time; }
}
