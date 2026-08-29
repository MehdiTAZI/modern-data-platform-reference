# Streaming pattern

## Contract
Every event is first represented as a replayable Bronze envelope containing the untouched payload and transport metadata. Parsing, business validation, referential checks and deduplication happen after Bronze.

## Azure reference path

```text
Producer -> Azure Event Hubs (Kafka endpoint)
         -> Access Connector managed identity
         -> Unity Catalog SERVICE credential
         -> Lakeflow Bronze streaming table
         -> Silver event-time watermark + event_id deduplication
         -> Gold real-time aggregates
```

The Kafka reader uses `databricks.serviceCredential`; no SASL password or connection string is embedded in code. The same Bronze contract can be fed by the file adapter for deterministic tests and replay.

## Delivery semantics
- Treat the transport as at-least-once.
- Require a stable `event_id` from the producer.
- Deduplicate in Silver using event time and a bounded watermark.
- Retain source offsets and raw payloads for audit/replay.
- Do not claim end-to-end exactly-once unless the producer, broker, transformation and sink semantics jointly prove it.

## Late data
The reference watermark is 30 minutes. Events beyond the business tolerance are observable and handled through explicit replay/reconciliation procedures rather than silently ignored.

## Failure modes to test
- duplicated event IDs;
- late events;
- malformed JSON;
- unknown dimensions/reference keys;
- schema evolution;
- source interruption and restart;
- replay of retained raw events.
