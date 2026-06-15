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
 * Source: schemas_yaml/marketdata/cdf_bar.yaml
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas.marketdata;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.inventzia.pulse.data.datum.Datum;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import org.jspecify.annotations.Nullable;

/**
 * Common data format (CDF) market data bar.
 *
 * <p>Type ID: {@value #TYPE_ID}
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record CdfBar(
    @JsonProperty("symb") String symb,
    @JsonProperty("timestamp") long timestamp,
    @JsonProperty("op") BigDecimal op,
    @JsonProperty("hi") BigDecimal hi,
    @JsonProperty("lo") BigDecimal lo,
    @JsonProperty("cl") BigDecimal cl,
    @JsonProperty("vlm") BigDecimal vlm,
    @JsonProperty("vwap") @Nullable BigDecimal vwap,
    @JsonProperty("datetime") Instant datetime,
    @JsonProperty("count") @Nullable Long count,
    @JsonProperty("date") LocalDate date,
    @JsonProperty("expiry") @Nullable String expiry,
    @JsonProperty("strike") @Nullable BigDecimal strike,
    @JsonProperty("symExp") @Nullable String symExp
) implements Datum {

    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.marketdata.CdfBar";
    public static final int    TYPE_VERSION = 1;

    @Override public String getDatumKey()  { return symb; }
    @Override public long   getDatumTime() { return timestamp; }
}
