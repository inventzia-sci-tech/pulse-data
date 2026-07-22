# Changelog

All notable changes to pulse-data are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
