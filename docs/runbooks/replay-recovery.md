# Runbook: Replay and Recovery
1. Identify affected dataset/time window and downstream consumers. 2. Stop conflicting writes. 3. Confirm raw/source retention and contract version. 4. Use a new checkpoint or bounded backfill flow. 5. Reconcile counts/keys/DQ metrics. 6. Publish recovery evidence. 7. Resume normal flow and document root cause.
