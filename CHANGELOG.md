# Changelog

All notable changes to pulse-data are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-24

### Added

- **`EngineStatus` datum** (`com.inventzia.pulse.data.schemas.platform.EngineStatus`), generated for
  both languages. Carries one lifecycle transition of an engine or gateway — `component`,
  `changedAt`, `fromStatus`, `toStatus` — on a constant routing key (`statusKey`), so a single
  subscriber observes a whole run's lifecycle from one registration. It lets pulse-beacon publish
  status as ordinary events rather than only as log lines, which in turn lets a viewer show a run's
  lifecycle in the same stream as its data, with no new record kind and no reader change.

  **Note for upgraders:** adding a type changes the provider manifest and therefore the run
  `typeFingerprint`. Recordings made before and after this release carry different fingerprints —
  that is the fingerprint doing its job, the type universe genuinely changed — and both sides of the
  cross-language bridge must be rebuilt from the same pulse-data.

### Changed

- **PyPI metadata repositioned as general-purpose.** Dropped the finance-specific classifiers
  (`Intended Audience :: Financial and Insurance Industry`, `Topic :: Office/Business :: Financial ::
  Investment`) for `Developers` / `Information Technology` / `Science/Research` and
  `Topic :: Software Development :: Libraries :: Python Modules`. Reworded the summary to lead with
  capabilities, and set capability-focused keywords (typed-events, code-generation, serialization,
  cross-language). Domain/finance positioning stays on the domain adapters.

## [0.2.3] - 2026-09-16

### Fixed

- **Obsolete `inventzia.pulse.data.schemas.registry` no longer ships.** The 0.2.2 wheel accidentally
  bundled a stale `schemas/registry.py` (the pre-SPI mutable, core-only registry) left over in a
  local `build/` tree; imported directly it bypassed extension discovery. The canonical registry is
  `inventzia.pulse.data.datum.registry` (composite, SPI-aware). Wheels are now built from a clean
  tree and content-checked, so the leftover cannot recur (see pulse-beacon `release-build.sh`).

## [0.2.2] - 2026-09-15

### Fixed

- **First published release.** 0.2.0 and 0.2.1 were tagged but never published; the 0.2.1 tag
  landed before the core provider was regenerated, so its wheels would bake `package_version`
  "0.2.0". 0.2.2 regenerates the provider to match the version and is the first release published to
  PyPI. No functional change from 0.2.1.

## [0.2.1] - 2026-09-15

### Fixed

- **PyPI project page.** README relative links are now absolute GitHub URLs (relative links do not
  resolve on PyPI), and `[project.urls]` gains `Repository` and `Changelog` so the PyPI sidebar
  links to the source. Documentation/metadata only; no code change from 0.2.0.

## [0.2.0] - 2026-09-13

### Fixed

- **Schema normalizer rejects ambiguous or malformed routing/version.** The manifest generator
  (`manifest.py`) now fails generation instead of silently accepting: more or fewer than one
  `x-datum-key` / `x-datum-time` (it took the last-annotated before, hiding a second key/time);
  a `required` entry that names no declared property; and a non-integer `x-version` (`int(1.9)`
  silently truncated to `1`, collapsing distinct versions). Existing schema fingerprints are
  unchanged (all core schemas already satisfy the stricter rules).
- **Registry validation now checks `TYPE_VERSION` for descriptor drift.** The composite registry
  validated a binding's `type_version` only as a positive integer; it now also requires it to equal
  the datum class's own `TYPE_VERSION` constant, mirroring the existing `TYPE_ID` drift check. A
  binding whose version silently disagrees with its class (a positive but drifted value) is rejected
  at construction, in both Python (`registry.py`) and Java (`DatumTypeRegistry`).

### Added

- **Schema manifest and composite fingerprint (SPI Phase 2).** Each provider now carries a
  baked, canonical manifest (`pdm1|<provider>|<TYPE_ID>:<version>:<sha256>;...`) computed by a
  shared generator module from the normalized wire-validation schema, so Python and Java bake
  byte-identical manifests. The composite registry retains immutable provider metadata
  (`providers()`), validates each manifest against its bindings at construction, and exposes a
  cross-language `fingerprint()` (or `None` with `unverifiable_providers()` when a provider
  predates Phase 2). The normalizer is a closed whitelist that fails generation on any
  unsupported wire-relevant construct rather than omitting it. A cross-language test asserts the
  Python and Java composite fingerprints are equal. Bridge startup gate and `RunInfo` recording
  are Phase 3.
- **Extensible datum types via a `DatumTypeProvider` SPI (Phase 1).** Independent packages
  can now contribute routed `Datum` types without modifying pulse-data. A provider declares
  a `provider_id` (reverse-DNS namespace root), `spi_version`, `package_version`, and
  `DatumTypeBinding` descriptors. The composite `DatumTypeRegistry` (Java) / `datum/registry.py`
  (Python) seeds the core provider directly and discovers extensions (Java `ServiceLoader`;
  Python `inventzia.pulse.datum_types` entry points), validates (duplicate IDs, namespace,
  descriptor drift, SPI/version rules, pydantic-model requirement, and more), then freezes an
  immutable registry. The generator now emits a `CoreDatumTypeProvider` instead of a static
  registry; the codec's public API is unchanged. Test-scoped isolation via
  `DatumTypeRegistry.of(...)` / `build_registry([...])` and `DatumCodec.forRegistry(...)` /
  `to_tagged_json(..., registry=)`. Manifest/fingerprint (cross-language equality gate) is
  reserved for Phase 2.
- **Encode-side registry validation (Python, parity with Java).** Generated
  `type_id_of` now verifies the class-to-`TYPE_ID` binding against the registry before
  tagged encoding, so a producer cannot emit an envelope whose `typeId` no runtime can
  decode (Java `typeIdOf` already did this). Groundwork for the extensible-datum SPI.
- **`TYPE_VERSION` sourced from the schema.** Both generators read an optional
  `x-version` (default 1) instead of hardcoding `1`, so a schema's wire version is
  declarable and can evolve. Cross-version compatibility enforcement lands with the SPI.
- `Datum` routing contract under `datum/` — Java interface (`getDatumKey()`,
  `getDatumTime()`) and Python `Protocol` equivalent.
- `DatumCodec` — the canonical JSON serializer for `Datum` types, exposed as a shared
  singleton (`DatumCodec.instance()`). Owns the JSON policy (JSR-310 java.time as ISO-8601,
  `BigDecimal`, ignore-unknown-properties); hides Jackson entirely. `DatumCodecException` for
  failures. Added the `jackson-datatype-jsr310` dependency the generated schemas require.
- YAML schemas under `schemas/schemas_yaml/`: `marketdata/cdf_bar.yaml`,
  `platform/heartbeat.yaml`, `platform/text_message.yaml`. Routing fields marked
  with `x-datum-key` / `x-datum-time`.
- Schema generators `generate_java.py` (immutable Java records implementing `Datum`,
  with `TYPE_ID` / `TYPE_VERSION`) and `generate_python.py` (Pydantic v2 models).
- Maven build (`pom.xml`) compiling the `Datum` interface and generated records.
- Dual-licensing files, DCO contribution policy, security and commercial docs, DCO workflow.
- `schemas/schemas_yaml/common/vector_value.yaml` — **`VectorValue`**, a generic timestamped
  vector of decimal observations with an optional parallel `valueIds` (a scalar value is the
  length-1 case).
- Generator **array support**: `type: array` fields generate immutable `List<X>` (Java) /
  `tuple[X, ...]` (Python).
- Generator **`x-parallel-to` constraint**: emits an equal-length validator for parallel
  arrays (e.g. `valueIds` must match `values`) — a Java record compact-constructor check and
  a Pydantic `model_validator`.

### Changed

- **Scope narrowed to the data definition only.** Pipelines, storage, FTP, parametrization,
  shared utilities, and Airflow orchestration moved out to the new **pulse-utils** repository,
  which depends on pulse-data (one-directional). pulse-data no longer pulls pandas, SQLAlchemy,
  or Airflow.
- Java package root standardised to `com.inventzia.pulse.data.*`; Python to
  `inventzia.pulse.data.*`.
- `py_environment_311.yml` (heavy: Airflow/pandas/SQLAlchemy) replaced by a minimal
  `py_environment.yml` (PyYAML, datamodel-code-generator, Pydantic). The heavy environment
  moved to pulse-utils.
- **`DatumCodec` serializes `BigDecimal` as a JSON string** (was a number), matching Python's
  `Decimal` output so exact decimals survive the cross-language boundary; the Python codec omits
  `None` fields (`exclude_none`) to match Java's `@JsonInclude(NON_NULL)`. Both fixed latent
  cross-language parity bugs surfaced by decimal / optional fields.
- **Generated datums are now genuinely immutable.** Java records take defensive `List.copyOf(...)`
  copies of list fields and `requireNonNull` required fields in a compact constructor; Python
  models are `frozen` with `tuple` (not `list`) sequences.
- **Decode rejects missing/null required fields** (parity with Python). Required record components
  are marked `@JsonProperty(required = true)` and the codec enables `FAIL_ON_NULL_FOR_PRIMITIVES`,
  so a missing or null required primitive (e.g. a timestamp) no longer silently deserializes to `0`.

### Removed

- Legacy `event_metadata.yaml` envelope and the `datumIntId` integer-id scheme.
- Obsolete generators (`autogenerate_schemas.py`, `autogenerate_schemas_with_fields.py`).

### Packaging & distribution

- **Installable `src/` layout + `pyproject.toml`.** The hand-written `datum/` and generated
  `schemas/` Python trees are merged into one `src/inventzia/pulse/data/`; `pip install pulse-data`
  works from a wheel with no repo checkout (setuptools, `find_namespace_packages`, Pydantic runtime,
  a `[generator]` extra for PyYAML, SPDX license).
- **PEP 420 namespace packages.** No `__init__.py` at `inventzia/` or `inventzia/pulse/` (the prefix
  is shared with pulse-beacon so the two install side by side); regular packages with deliberate
  exports below, so `from inventzia.pulse.data.datum import Datum` resolves.
- **Generator defaults are script-relative**, targeting the `src/` tree — a bare
  `python generate_python.py` regenerates the canonical location from any directory (the removed
  `schemas_py/` is no longer recreated).
- `pom.xml` gains release metadata (project URL, developers) and an opt-in `release` profile that
  attaches source + javadoc jars.
- **CI** (`.github/workflows/ci.yml`): `mvn verify` from a clean environment, plus a Python job that
  builds the wheel, clean-installs it, checks the documented imports and PEP 420 namespace, and
  asserts both Python and Java regeneration are diff-clean.
