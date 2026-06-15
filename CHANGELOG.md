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

### Removed

- Legacy `event_metadata.yaml` envelope and the `datumIntId` integer-id scheme.
- Obsolete generators (`autogenerate_schemas.py`, `autogenerate_schemas_with_fields.py`).
