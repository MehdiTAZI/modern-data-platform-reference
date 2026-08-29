# Data Flow

Files enter a governed external landing volume and are incrementally ingested with Auto Loader. Order events use a source-neutral raw envelope; the demo reads retained JSON lines while the production adapter can read Kafka/Event Hubs. Bronze preserves source payload/metadata, Silver applies contracts/dedup/conformance, Gold publishes consumer semantics.
