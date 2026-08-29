# Reference NFRs

These are design targets, not benchmark claims.

| NFR | Target |
|---|---|
| Streaming freshness | p95 < 5 min |
| Batch freshness | < 60 min after source arrival |
| Pipeline success | >= 99.5% scheduled runs |
| DQ visibility | 100% quarantined rows have explicit reasons |
| Replay | raw/source retention sufficient for 30-day operational replay |
| RPO | <= 15 min for streaming source events when source retains data |
| RTO | <= 4 h for regional service recovery plan |
| Security | no long-lived credentials committed to Git |
| Cost | workload/domain attribution via tags/system tables |
