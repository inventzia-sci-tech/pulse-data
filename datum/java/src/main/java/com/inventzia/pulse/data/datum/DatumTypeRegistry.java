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

import com.inventzia.pulse.data.schemas.CoreDatumTypeProvider;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.ServiceLoader;

/**
 * The composite datum-type registry: {@code TYPE_ID <-> } model class.
 *
 * <p>Built once from the core provider (seeded directly) plus discovered extension
 * providers, validated, then frozen. The tagged {@link DatumCodec} resolves types through
 * it. This is hand-written infrastructure; the per-provider bindings are generated. Mirror
 * of the Python {@code registry.py}.
 *
 * <p>Core is instantiated directly, never via {@link ServiceLoader}, so a source-tree or
 * mis-packaged install cannot lose its core types and core-only parity is guaranteed.
 */
public final class DatumTypeRegistry {

    /** The SPI contract version this pulse-data supports. Providers must match it exactly. */
    public static final int SPI_VERSION = 1;

    private final Map<String, Class<? extends Datum>> byId;
    private final Map<Class<? extends Datum>, String> byClass;

    private DatumTypeRegistry(Map<String, Class<? extends Datum>> byId,
                             Map<Class<? extends Datum>, String> byClass) {
        this.byId = byId;
        this.byClass = byClass;
    }

    /** @return the model class registered for a {@code TYPE_ID}. */
    public Class<? extends Datum> classFor(String typeId) {
        Class<? extends Datum> type = byId.get(typeId);
        if (type == null) {
            throw new IllegalArgumentException("Unknown TYPE_ID: " + typeId);
        }
        return type;
    }

    /**
     * @return the {@code TYPE_ID} for a datum instance, verified against the registry, so a
     *         producer cannot emit an envelope whose {@code typeId} no runtime can decode.
     */
    public String typeIdOf(Datum datum) {
        String typeId = byClass.get(datum.getClass());
        if (typeId == null) {
            throw new IllegalArgumentException("Unregistered datum type: " + datum.getClass().getName());
        }
        return typeId;
    }

    // ------------------------------------------------------------------
    // Construction
    // ------------------------------------------------------------------

    /** Build an isolated registry from an explicit provider list (for tests / custom universes). */
    public static DatumTypeRegistry of(DatumTypeProvider... providers) {
        return build(List.of(providers));
    }

    /** Build an isolated registry from an explicit provider list. */
    public static DatumTypeRegistry of(List<DatumTypeProvider> providers) {
        return build(providers);
    }

    /** The process-wide composite registry, built once (lazily) and frozen. */
    public static DatumTypeRegistry defaultRegistry() {
        return Holder.INSTANCE;
    }

    /** Initialization-on-demand holder: builds the discovered registry on first use. */
    private static final class Holder {
        private static final DatumTypeRegistry INSTANCE = build(discover());
    }

    private static List<DatumTypeProvider> discover() {
        List<DatumTypeProvider> providers = new ArrayList<>();
        providers.add(new CoreDatumTypeProvider());   // core seeded directly, never discovered
        List<DatumTypeProvider> extensions = new ArrayList<>();
        for (DatumTypeProvider p : ServiceLoader.load(DatumTypeProvider.class)) {
            extensions.add(p);
        }
        extensions.sort(Comparator.comparing(DatumTypeProvider::providerId));
        providers.addAll(extensions);
        return providers;
    }

    private static DatumTypeRegistry build(List<DatumTypeProvider> providers) {
        Map<String, Class<? extends Datum>> byId = new HashMap<>();
        Map<Class<? extends Datum>, String> byClass = new HashMap<>();
        java.util.Set<String> seenProviderIds = new java.util.HashSet<>();

        for (DatumTypeProvider provider : providers) {
            if (provider == null) {
                fail("a provider is null");
            }
            String pid = provider.providerId();
            if (pid == null || pid.isBlank() || !pid.matches("[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)+")) {
                fail("provider has an empty or malformed providerId: " + pid);
            }
            if (!seenProviderIds.add(pid)) {
                fail("duplicate providerId '" + pid + "'");
            }
            if (provider.spiVersion() != SPI_VERSION) {
                fail("provider '" + pid + "' targets SPI version " + provider.spiVersion()
                        + ", this pulse-data supports " + SPI_VERSION);
            }
            String pv = provider.packageVersion();
            if (pv == null || pv.isBlank()) {
                fail("provider '" + pid + "' has a missing or blank packageVersion");
            }

            Collection<DatumTypeBinding> raw = provider.bindings();
            if (raw == null) {
                fail("provider '" + pid + "' returned a null bindings collection");
            }
            List<DatumTypeBinding> bindings = new ArrayList<>(raw);
            bindings.sort(Comparator.comparing(b -> b.typeId() == null ? "" : b.typeId()));
            if (bindings.isEmpty()) {
                fail("provider '" + pid + "' contributes no datum types");
            }

            java.util.Set<Class<?>> providerClasses = new java.util.HashSet<>();
            for (DatumTypeBinding b : bindings) {
                if (b == null) {
                    fail("provider '" + pid + "' has a null binding");
                }
                if (b.typeId() == null || b.typeId().isBlank()) {
                    fail("provider '" + pid + "' has an empty or malformed typeId");
                }
                if (!b.typeId().startsWith(pid + ".")) {
                    fail("provider '" + pid + "' type '" + b.typeId()
                            + "' is not under its namespace '" + pid + ".'");
                }
                if (b.datumClass() == null) {
                    fail("provider '" + pid + "' type '" + b.typeId() + "' has a null class");
                }
                if (b.typeVersion() <= 0) {
                    fail("provider '" + pid + "' type '" + b.typeId()
                            + "': TYPE_VERSION must be positive, got " + b.typeVersion());
                }
                // Descriptor drift: the binding must match the class's own TYPE_ID constant.
                // Reflection here is once, at construction, not on the encode/decode hot path.
                String classTypeId = readTypeIdConstant(pid, b);
                if (!b.typeId().equals(classTypeId)) {
                    fail("provider '" + pid + "': binding typeId '" + b.typeId()
                            + "' does not match " + b.datumClass().getName() + ".TYPE_ID '"
                            + classTypeId + "' (descriptor drift)");
                }
                if (!providerClasses.add(b.datumClass())) {
                    fail("provider '" + pid + "' binds class " + b.datumClass().getName() + " more than once");
                }
                if (byId.containsKey(b.typeId())) {
                    fail("duplicate TYPE_ID '" + b.typeId() + "' (provider '" + pid
                            + "' conflicts with an earlier provider)");
                }
                if (byClass.containsKey(b.datumClass())) {
                    fail("class " + b.datumClass().getName() + " is bound to more than one TYPE_ID");
                }
                byId.put(b.typeId(), b.datumClass());
                byClass.put(b.datumClass(), b.typeId());
            }
        }
        return new DatumTypeRegistry(Map.copyOf(byId), Map.copyOf(byClass));
    }

    private static String readTypeIdConstant(String pid, DatumTypeBinding b) {
        try {
            return (String) b.datumClass().getField("TYPE_ID").get(null);
        } catch (ReflectiveOperationException e) {
            fail("provider '" + pid + "' type '" + b.typeId() + "': class "
                    + b.datumClass().getName() + " has no accessible TYPE_ID constant");
            return null; // unreachable
        }
    }

    private static void fail(String msg) {
        throw new IllegalStateException("invalid datum-type registry: " + msg);
    }
}
