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
 * Source: schemas_yaml/platform/heartbeat.yaml
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas.platform;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.inventzia.pulse.data.datum.Datum;

/**
 * Periodic platform heartbeat produced by HeartBeatGateway. Actors subscribe to a heartbeat Topic to implement periodic behaviour (analytics windows, timeout checks) that fires at regular simulation-time intervals regardless of whether domain events arrive in that interval.
 *
 * <p>Type ID: {@value #TYPE_ID}
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record HeartBeat(
    @JsonProperty("beatKey") String beatKey,
    @JsonProperty("beatTime") long beatTime
) implements Datum {

    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.platform.HeartBeat";
    public static final int    TYPE_VERSION = 1;

    @Override public String getDatumKey()  { return beatKey; }
    @Override public long   getDatumTime() { return beatTime; }
}
