# Pattern: Replay

Replay starts from retained raw/source data, not from manually edited Silver tables. Use bounded source windows, isolated checkpoints, stable business/event keys and reconciliation before promotion.

For ordinary late arrivals, prefer the automated reconciliation pattern: the stream stays bounded by its watermark while `orders_canonical` recovers validated late events from Bronze. Full replay is reserved for wider incidents such as broken transformation logic, corrupted checkpoints or historical contract reprocessing.

A replay must record the source window, code/contract version, checkpoint strategy, expected duplicate boundary and reconciliation result. See the replay runbook, the late-event reconciliation pattern and ADR-017.
