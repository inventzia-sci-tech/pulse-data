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

/**
 * Routing contract for all data types transported on the pulse-beacon bus.
 *
 * <p>Every schema defined in pulse-data generates a class that implements
 * this interface. The schema designer decides which domain fields carry
 * routing semantics by annotating them with {@code x-datum-key: true} and
 * {@code x-datum-time: true} in the YAML source.
 *
 * <p>Examples:
 * <ul>
 *   <li>A market data bar: key = instrument symbol, time = bar timestamp.</li>
 *   <li>A heartbeat: key = beat identifier, time = scheduled beat time.</li>
 *   <li>An order fill: key = order ID, time = fill execution time.</li>
 * </ul>
 *
 * <p>The pulse-beacon engine reads {@link #getDatumKey()} and
 * {@link #getDatumTime()} to route and order events in the
 * {@code TimeMachine}. No other knowledge of the payload structure
 * is required at the infrastructure level.
 *
 * <p>In Python, this contract is expressed as a {@code Protocol} in
 * {@code inventzia.pulse.data.datum} and satisfied structurally — generated
 * Pydantic models expose {@code datum_key} and {@code datum_time} properties.
 */
public interface Datum {

    /**
     * The routing key for this datum instance.
     *
     * <p>Identifies the specific entity this datum relates to within its
     * topic — for example an instrument symbol, a session ID, or a tenant.
     * Must not be {@code null}; return an empty string when no key applies.
     *
     * @return the routing key; never {@code null}
     */
    String getDatumKey();

    /**
     * The logical time of this datum, in epoch milliseconds.
     *
     * <p>Represents when the underlying event occurred — not when it was
     * published or received. The {@code TimeMachine} uses this value to
     * order events from multiple sources into a single causal stream.
     *
     * @return epoch milliseconds of the datum's logical time
     */
    long getDatumTime();
}
