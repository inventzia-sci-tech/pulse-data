# pulse-data

**pulse-data** is the single source of truth for the data types that flow across the Pulse
platform. Every event type is defined once in YAML and code-generated into strongly-typed,
immutable classes for both Java and Python. There is no hand-written serialisation code and no
way for the two language bindings to drift apart — they are projections of the same schema.

A consumer of pulse-data gets two things: a small, stable **routing contract** (`Datum`) that the
transport layer depends on, and a growing set of **generated data classes** that implement it.

This repository is deliberately narrow. It contains *only* the data definition — the contract,
the schemas, and the generators. It pulls no pandas, no SQLAlchemy, no Airflow. Anything that
*uses* the data (ingestion pipelines, storage backends, orchestration, shared helpers) lives in
**[pulse-utils](https://github.com/inventzia-sci-tech/pulse-utils)** and depends on pulse-data,
never the other way round.

---

## What lives here

| Area | Path | What it is |
|------|------|-----------|
| Routing contract | `datum/` | Hand-written `Datum` interface (Java) and `Protocol` (Python). The stable API everything else conforms to. |
| JSON serializer | `datum/` | `DatumCodec` (Java) and `datum/codec.py` (Python) — the canonical, shared serializer for `Datum` types (see below). |
| Schema sources | `schemas/schemas_yaml/` | YAML definitions — the single source of truth. |
| Generated Java | `schemas/schemas_java/` | Immutable Java `record` classes under `com.inventzia.pulse.data.schemas`. Build artefact; do not edit. |
| Generated Python | `schemas/schemas_py/` | Pydantic v2 models under `inventzia.pulse.data.schemas` (mirrors Java). Build artefact; do not edit. |
| Type registry | both | Generated `DatumTypeRegistry` (Java) / `schemas/registry.py` (Python): `TYPE_ID → class`, for self-describing decode. |
| Generators | `schemas/schemas-generators/` | `generate_java.py`, `generate_python.py`. |

Everything here is light: the Java side compiles to a small jar (Jackson + JSpecify only); the
Python side needs just PyYAML, datamodel-code-generator, and Pydantic.

---

## Core idea: schema → routing-aware data class

A schema is plain JSON-Schema (draft-07) in YAML, with two pulse-specific annotations that mark
which fields carry routing meaning:

```yaml
# schemas/schemas_yaml/marketdata/cdf_bar.yaml
$id: "com.inventzia.pulse.data.schemas.marketdata.CdfBar"
title: CdfBar
type: object
properties:
  symb:
    type: string
    x-datum-key: true        # this field is the routing key
  timestamp:
    type: integer
    format: int64
    x-datum-time: true       # this field is the logical event time
  op:    { type: number, format: decimal }
  # ... more fields ...
required: [symb, timestamp, op]
```

From this, the generators produce classes that implement the `Datum` contract by delegating to the
annotated fields:

**Java** (`schemas_java/.../CdfBar.java`) — an immutable record:
```java
public record CdfBar(String symb, long timestamp, BigDecimal op /* ... */)
        implements Datum {
    public static final String TYPE_ID      = "com.inventzia.pulse.data.schemas.marketdata.CdfBar";
    public static final int    TYPE_VERSION = 1;
    @Override public String getDatumKey()  { return symb; }
    @Override public long   getDatumTime() { return timestamp; }
}
```

**Python** (`schemas_py/inventzia/pulse/data/schemas/marketdata/cdf_bar.py`) — a Pydantic v2 model
satisfying the `Datum` protocol:
```python
class CdfBar(BaseModel):
    TYPE_ID:      ClassVar[str] = "com.inventzia.pulse.data.schemas.marketdata.CdfBar"
    TYPE_VERSION: ClassVar[int] = 1
    symb: str
    timestamp: int
    # ...
    @property
    def datum_key(self) -> str:  return self.symb
    @property
    def datum_time(self) -> int: return self.timestamp
```

---

## Design decisions

- **YAML is the only source of truth.** Field definitions exist in exactly one place. Java and
  Python are generated, never hand-edited. Regenerate after every schema change.

- **`$id` is the type identity.** Each schema's `$id` is the fully-qualified class name and becomes
  the `TYPE_ID` constant in both languages — the single discriminator used for routing and
  deserialisation. There is no separate numeric id to keep in sync.

- **The `Datum` contract is minimal.** Two methods — `getDatumKey()` and `getDatumTime()` — are all
  the transport layer needs to route and time-order data. The schema author decides which domain
  fields fulfil them via `x-datum-key` / `x-datum-time`. Nothing else about the payload is exposed
  to the infrastructure.

- **Data classes are immutable.** Java records and frozen-by-convention Pydantic models. A value on
  the bus cannot be mutated by one consumer and observed changed by another.

- **JSON is the wire format.** Java (Jackson) and Python (Pydantic) serialise to and from the same
  JSON, so a value produced in one language is consumed verbatim in the other.

- **Serialization is owned here, not by callers.** Because pulse-data owns the types and schemas,
  it also owns how a `Datum` becomes JSON. `DatumCodec` is the canonical serializer, a shared
  singleton (`DatumCodec.instance()`), with `toJson(Datum)` / `fromJson(json, type)` as its whole
  surface. It configures the JSON policy *once* for every field type the schemas use — JSR-310
  `java.time` written as ISO-8601, `BigDecimal` for exact decimals, unknown properties ignored on
  read for forward compatibility — and hides the underlying engine (Jackson) entirely. Consumers
  never construct or pass a JSON mapper; downstream code (e.g. pulse-beacon's gateways) uses the
  singleton and never references Jackson.

  Two forms are offered. **Type-directed** (`toJson` / `fromJson(json, Class)`) when the caller
  knows the concrete class — e.g. it knows a topic's payload type. **Self-describing** (`toTaggedJson`
  / `fromTaggedJson`) wraps the value in an envelope `{"typeId": "<TYPE_ID>", "payload": {…}}`, so a
  receiver can recover the type from the message itself wherever it isn't known ahead of time — the
  in-process cross-language bridge, and later the socket/ZMQ transport. The class is resolved through
  a generated `TYPE_ID → class` registry (`DatumTypeRegistry` in Java, `schemas/registry.py` in
  Python) — the modern, code-generated form of the old hand-maintained datum-id factory. The same
  envelope is produced and consumed identically in both languages.

- **Python uses structural typing.** The Python `Datum` is a `Protocol`; generated models satisfy
  it by exposing `datum_key` / `datum_time` properties — no inheritance, no import coupling.

---

## Adding a new data type

1. Create a YAML schema under `schemas/schemas_yaml/<area>/`, with a unique `$id`, a `title`
   (becomes the class name), and exactly one `x-datum-key` and one `x-datum-time` field.
2. Regenerate both bindings:
   ```bash
   cd schemas/schemas-generators
   conda run -n pulse-data python generate_java.py
   conda run -n pulse-data python generate_python.py
   ```
3. Commit the YAML **and** the regenerated Java/Python output.

See [`schemas/schemas-generators/readme.md`](./schemas/schemas-generators/readme.md) for generator
options (paths, dry-run, verbose).

---

## Environment

The Python generators run in the minimal conda environment defined by
[`py_environment.yml`](./py_environment.yml):

```bash
conda env create -f py_environment.yml
conda activate pulse-data
```

Java sources (the `Datum` interface and generated records) build with Maven via
[`pom.xml`](./pom.xml); Java 17+.

---

## Licensing

Dual-licensed:

- **Open Source (AGPL v3.0 or later)** — see [`LICENSE-AGPL-3.0`](./LICENSE-AGPL-3.0).
- **Commercial License** — see [`COMMERCIAL.md`](./COMMERCIAL.md) for the summary and
  [`LICENSE-COMMERCIAL.txt`](./LICENSE-COMMERCIAL.txt) for the binding terms.

Contact operations@inventzia.com for commercial licensing.

## Contributing

By submitting a contribution you agree to [`CLA.md`](./CLA.md), including the Developer Certificate
of Origin sign-off and the dual-licensing grant. CI enforces DCO sign-off on every PR commit.

## Security

Report vulnerabilities privately per [`SECURITY.md`](./SECURITY.md). Do not open public issues for
security problems.

## Trademarks

"Pulse" and "Inventzia" are trademarks of Inventzia Science and Technology Ltd. The licenses for
this software do not grant any rights to use these trademarks.
