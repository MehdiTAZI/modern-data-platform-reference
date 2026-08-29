-- Lakeflow Jobs reliability
SELECT workspace_id, job_id, result_state, count(*) runs FROM system.lakeflow.job_run_timeline WHERE period_start_time >= current_timestamp() - INTERVAL 7 DAYS GROUP BY ALL ORDER BY runs DESC;
