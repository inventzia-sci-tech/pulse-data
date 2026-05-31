# pulse-data

**pulse-data** is the single source of truth for event and data schemas used across the Pulse
platform. Schemas are defined once in YAML and code-generated into strongly-typed classes for
both Java and Python. This eliminates hand-written serialisation code, prevents language-side
drift, and makes schema versioning explicit.

## Design intent

The old approach — hand-written Java base classes with CSV serialisation and Python wrappers via
a Java bridge — was fragile: field definitions lived in three places, positional CSV broke on
comma-containing values, and a Java package rename could break Python at import. pulse-data
replaces all of that with a single YAML definition per event type, from which everything else is
derived.

Generated Java classes implement `com.inventzia.beacon.core.Event` (from
[pulse-beacon](https://github.com/inventzia-sci-tech/pulse-beacon)) and are annotated for Jackson
serialisation. Generated Python classes are Pydantic models. Both sides deserialise the same JSON
wire format.

## Repository structure

```
pulse-data/
├── schemas/
│   ├── schemas_yaml/          # YAML source of truth (JSON Schema draft-07)
│   │   ├── event_metadata.yaml
│   │   └── marketdata/
│   │       └── cdf_bar.yaml
│   ├── schemas_java/          # Code-generated Java classes (do not edit by hand)
│   ├── schemas_py/            # Code-generated Python Pydantic models (do not edit by hand)
│   └── schemas-generators/    # Generation scripts and instructions
├── pipelines/                 # Python data pipeline base classes (DataPipeline)
├── storage/
│   ├── file/                  # File-based storage implementation
│   └── sqldb/                 # SQL-based storage implementation
├── commons/
│   ├── ftp/                   # FTP utilities
│   ├── parametrization/       # Config/parametrization helpers
│   └── utils/                 # Shared utilities
└── airflow_pipelines/         # Airflow DAG templates for pipeline orchestration
```

> **Note:** The generated directories (`schemas_java/`, `schemas_py/`) are committed for
> convenience but should be treated as build artefacts. Always regenerate after editing YAML.

## Defining a new event schema

1. Create a YAML file under `schemas/schemas_yaml/` following JSON Schema draft-07.
2. Extend `event_metadata.yaml` via `$ref` for the standard routing and timestamp fields
   (`datumKey`, `datumTimestamp`, `datumPublishedTime`, `datumReceivedTime`, `eventVersion`).
3. Run the generators (see `schemas/schemas-generators/`) to produce Java and Python classes.
4. The generated Java class must implement `com.inventzia.beacon.core.Event` and declare
   `public static final String TYPE_ID` equal to the schema `$id`. This is validated by
   `Topic<E>` at construction time.

See [`schemas/schemas-generators/readme.md`](./schemas/schemas-generators/readme.md) for
step-by-step generation instructions.

## Schema versioning

Every event schema should include an `eventVersion` integer field. Gateways and engines use this
for compatibility checks when producers and consumers are built at different times. Increment the
version when making a breaking change to a schema; add new optional fields without incrementing.

## Known open issues

- `event_metadata.yaml` still carries `datumIntId` — a legacy field from the old integer-ID
  system. This will be removed; type identity is now the `typeId()` string from the schema `$id`.
- The envelope+payload split (`EventMetadata` wrapping a free-form `EventPayload`) will be
  replaced with per-event flat schemas that compose the base metadata fields via `$ref`.
- A Java ↔ Python round-trip test (serialise in Java, deserialise in Python, compare) is planned
  but not yet written.

## Licensing

This project is dual-licensed:

- **Open Source (AGPL v3.0 or later)** — see [`LICENSE-AGPL-3.0`](./LICENSE-AGPL-3.0).
- **Commercial License** — see [`COMMERCIAL.md`](./COMMERCIAL.md) for the informational summary
  and [`LICENSE-COMMERCIAL.txt`](./LICENSE-COMMERCIAL.txt) for the binding terms.

Contact: operations@inventzia.com for commercial licensing.

## Contributing

Contributions are welcome. By submitting a contribution you agree to the terms in
[`CLA.md`](./CLA.md), including the Developer Certificate of Origin sign-off and the
dual-licensing grant. CI enforces DCO sign-off on every PR commit.

## Security

Please report security vulnerabilities privately as described in [`SECURITY.md`](./SECURITY.md).
Do not open public issues for security problems.

## Trademarks

"Pulse" and "Inventzia" are trademarks of Inventzia Science and Technology Ltd. The licenses for
this software do not grant any rights to use these trademarks.
