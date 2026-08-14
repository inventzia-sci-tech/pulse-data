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

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.ServiceLoader;
import java.util.Set;
import java.util.regex.Pattern;

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

    private static final String MANIFEST_FORMAT = "pdm1";
    private static final Pattern HEX64 = Pattern.compile("[0-9a-f]{64}");

    /** One parsed manifest entry: TYPE_ID, TYPE_VERSION, and per-type fingerprint. */
    public record TypeEntry(String typeId, int typeVersion, String fingerprint) {}

    /** Retained, immutable metadata for one contributing provider (diagnostics / audit). */
    public record ProviderInfo(String providerId, String packageVersion,
                               String manifest, List<TypeEntry> entries) {}

    private final Map<String, Class<? extends Datum>> byId;
    private final Map<Class<? extends Datum>, String> byClass;
    private final List<ProviderInfo> providers;

    private DatumTypeRegistry(Map<String, Class<? extends Datum>> byId,
                             Map<Class<? extends Datum>, String> byClass,
                             List<ProviderInfo> providers) {
        this.byId = byId;
        this.byClass = byClass;
        this.providers = providers;
    }

    /** @return an immutable {@link ProviderInfo} snapshot for every contributing provider, in order. */
    public List<ProviderInfo> providers() {
        return providers;
    }

    /** @return provider IDs with no manifest (predating Phase 2); a fingerprint cannot include them. */
    public List<String> unverifiableProviders() {
        List<String> out = new ArrayList<>();
        for (ProviderInfo p : providers) {
            if (p.manifest() == null) out.add(p.providerId());
        }
        return List.copyOf(out);
    }

    /**
     * @return the SHA-256 hex of the providers' manifests (sorted by providerId), or {@code null}
     *         if any provider is unverifiable (see {@link #unverifiableProviders()}). {@code null}
     *         is treated as fail-closed by the cross-language bridge.
     */
    public String fingerprint() {
        List<ProviderInfo> ordered = new ArrayList<>(providers);
        ordered.sort(Comparator.comparing(ProviderInfo::providerId));
        StringBuilder joined = new StringBuilder();
        for (int i = 0; i < ordered.size(); i++) {
            if (ordered.get(i).manifest() == null) return null;
            if (i > 0) joined.append('\n');
            joined.append(ordered.get(i).manifest());
        }
        return sha256Hex(joined.toString());
    }

    private static String sha256Hex(String s) {
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(hash.length * 2);
            for (byte b : hash) sb.append(Character.forDigit((b >> 4) & 0xF, 16)).append(Character.forDigit(b & 0xF, 16));
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
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

    /**
     * Runs the datum-type SPI discovery and returns the process-wide composite registry: the core
     * provider seeded directly, plus every extension {@link DatumTypeProvider} found on the
     * classpath via {@link ServiceLoader}, validated and frozen.
     *
     * <p>Idempotent: the registry is built once and cached. Call this at a deterministic point
     * (e.g. engine startup) to establish the type universe <em>explicitly</em>, instead of letting
     * it be bootstrapped as a side effect of the first observability read. Returns the same
     * instance as {@link #defaultRegistry()} — the two differ only in intent: this one names and
     * performs the discovery step, the other is the plain accessor.
     */
    public static DatumTypeRegistry discoverProviders() {
        return Holder.INSTANCE;
    }

    /** The process-wide composite registry, built once (lazily) and frozen. */
    public static DatumTypeRegistry defaultRegistry() {
        return Holder.INSTANCE;
    }

    /** Initialization-on-demand holder: builds the discovered registry on first use. */
    private static final class Holder {
        private static final DatumTypeRegistry INSTANCE = build(loadProviders());
    }

    /**
     * The SPI discovery itself: seed the core provider directly, then load every extension
     * {@link DatumTypeProvider} advertised on the classpath via {@link ServiceLoader}, ordered by
     * provider id. Invoked once by {@link Holder}; call {@link #discoverProviders()} to trigger it.
     */
    private static List<DatumTypeProvider> loadProviders() {
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
        Set<String> seenProviderIds = new HashSet<>();
        List<ProviderInfo> providerInfos = new ArrayList<>();

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

            providerInfos.add(parseManifest(provider, bindings));
        }
        return new DatumTypeRegistry(Map.copyOf(byId), Map.copyOf(byClass), List.copyOf(providerInfos));
    }

    /** Parse and validate a provider's baked manifest against its bindings (see the SPI spec). */
    private static ProviderInfo parseManifest(DatumTypeProvider provider, List<DatumTypeBinding> bindings) {
        String pid = provider.providerId();
        Optional<String> mo = provider.manifest();
        if (mo.isEmpty()) {
            return new ProviderInfo(pid, provider.packageVersion(), null, List.of());
        }
        String m = mo.get();
        if (m.indexOf('\n') >= 0 || m.indexOf('\r') >= 0) {
            fail("provider '" + pid + "' manifest contains a newline");
        }
        String[] parts = m.split("\\|", -1);
        if (parts.length != 3 || !parts[0].equals(MANIFEST_FORMAT)) {
            fail("provider '" + pid + "' manifest is not a " + MANIFEST_FORMAT + " manifest");
        }
        if (!parts[1].equals(pid)) {
            fail("provider '" + pid + "' manifest embeds provider id '" + parts[1] + "'");
        }
        List<TypeEntry> entries = new ArrayList<>();
        List<String> typeIds = new ArrayList<>();
        if (!parts[2].isEmpty()) {
            for (String entry : parts[2].split(";", -1)) {
                String[] f = entry.split(":", -1);
                if (f.length != 3) {
                    fail("provider '" + pid + "' manifest has a malformed entry '" + entry + "'");
                }
                if (!HEX64.matcher(f[2]).matches()) {
                    fail("provider '" + pid + "' type '" + f[0] + "': fingerprint is not 64 lowercase hex");
                }
                int ver;
                try {
                    ver = Integer.parseInt(f[1]);
                } catch (NumberFormatException e) {
                    fail("provider '" + pid + "' type '" + f[0] + "': non-integer version '" + f[1] + "'");
                    return null; // unreachable
                }
                entries.add(new TypeEntry(f[0], ver, f[2]));
                typeIds.add(f[0]);
            }
        }
        List<String> sorted = new ArrayList<>(typeIds);
        sorted.sort(Comparator.naturalOrder());
        if (!typeIds.equals(sorted)) {
            fail("provider '" + pid + "' manifest entries are not sorted by TYPE_ID");
        }
        if (new HashSet<>(typeIds).size() != typeIds.size()) {
            fail("provider '" + pid + "' manifest has duplicate entries");
        }
        Map<String, Integer> bindingVer = new HashMap<>();
        for (DatumTypeBinding b : bindings) bindingVer.put(b.typeId(), b.typeVersion());
        Map<String, Integer> entryVer = new HashMap<>();
        for (TypeEntry e : entries) entryVer.put(e.typeId(), e.typeVersion());
        if (!bindingVer.keySet().equals(entryVer.keySet())) {
            fail("provider '" + pid + "' manifest does not match its bindings one-to-one");
        }
        for (Map.Entry<String, Integer> e : entryVer.entrySet()) {
            if (!bindingVer.get(e.getKey()).equals(e.getValue())) {
                fail("provider '" + pid + "' type '" + e.getKey() + "': manifest version " + e.getValue()
                        + " != binding version " + bindingVer.get(e.getKey()));
            }
        }
        return new ProviderInfo(pid, provider.packageVersion(), m, List.copyOf(entries));
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
