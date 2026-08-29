-- Pipeline event-log discovery/operations starter. Adapt to the event-log table shared by your pipeline.
SELECT * FROM system.lakeflow.pipeline_update_timeline WHERE period_start_time >= current_timestamp() - INTERVAL 24 HOURS ORDER BY period_start_time DESC;
