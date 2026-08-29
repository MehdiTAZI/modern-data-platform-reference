# End-to-End Data Flow

## Batch

```text
Source snapshot/increment
  -> landing
  -> Bronze Delta
  -> validation + deduplication
  -> Silver Delta
  -> business transformation
  -> Gold data product
```

## Streaming

```text
Event producer
  -> broker/event service
  -> Structured Streaming
  -> Bronze Delta + checkpoint
  -> stateful validation/deduplication
  -> Silver Delta
  -> streaming/near-real-time Gold
```

## Operational metadata

Every production ingestion should capture at least:

- source identifier;
- ingestion timestamp;
- source event/update timestamp where available;
- pipeline/run identifier;
- source file or stream metadata;
- schema/version information where applicable.
