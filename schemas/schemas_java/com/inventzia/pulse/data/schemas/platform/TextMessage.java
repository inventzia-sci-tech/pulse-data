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
 * Source: schemas_yaml/platform/text_message.yaml
 * Regenerate: python schemas/schemas-generators/generate_java.py
 */

package com.inventzia.pulse.data.schemas.platform;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.inventzia.pulse.data.datum.Datum;
import java.util.Objects;

/**
 * Generic carrier for a free-text string payload. The platform equivalent of a plain message — useful for diagnostics, echo/relay examples, and any actor or gateway that needs to move arbitrary text on a topic.
 *
 * <p>Type ID: {@value #TYPE_ID}
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record TextMessage(
    @JsonProperty(value = "msgKey", required = true) String msgKey,
    @JsonProperty(value = "msgTime", required = true) long msgTime,
    @JsonProperty(value = "text", required = true) String text
) implements Datum {

    public TextMessage {
        msgKey = Objects.requireNonNull(msgKey, "msgKey");
        text = Objects.requireNonNull(text, "text");
    }

    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.platform.TextMessage";
    public static final int    TYPE_VERSION = 1;

    @Override public String getDatumKey()  { return msgKey; }
    @Override public long   getDatumTime() { return msgTime; }
}
