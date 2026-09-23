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
 * Source: schemas_yaml/platform/engine_status.yaml
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas.platform;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.inventzia.pulse.data.datum.Datum;
import java.util.Objects;

/**
 * A lifecycle transition of the engine or one of its gateways, published as an ordinary event on the engine's status topic so that recorders, viewers and actors observe a run's lifecycle through the same mechanism they observe its data. Emitted on every status change: the component that changed, the status it left, and the status it entered.
 * Status is a control-plane fact about the run rather than domain data, so it is delivered directly to subscribers at the moment of the change rather than scheduled through the TimeMachine. That is deliberate: the first transitions happen before the dispatch barrier opens and the last after the dispatch loop has ended, so a status event routed through the queue would lose exactly the transitions that matter most.
 *
 * <p>Type ID: {@value #TYPE_ID}
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record EngineStatus(
    @JsonProperty(value = "statusKey", required = true) String statusKey,
    @JsonProperty(value = "component", required = true) String component,
    @JsonProperty(value = "changedAt", required = true) long changedAt,
    @JsonProperty(value = "fromStatus", required = true) String fromStatus,
    @JsonProperty(value = "toStatus", required = true) String toStatus
) implements Datum {

    public EngineStatus {
        statusKey = Objects.requireNonNull(statusKey, "statusKey");
        component = Objects.requireNonNull(component, "component");
        fromStatus = Objects.requireNonNull(fromStatus, "fromStatus");
        toStatus = Objects.requireNonNull(toStatus, "toStatus");
    }

    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.platform.EngineStatus";
    public static final int    TYPE_VERSION = 1;

    @Override public String getDatumKey()  { return statusKey; }
    @Override public long   getDatumTime() { return changedAt; }
}
