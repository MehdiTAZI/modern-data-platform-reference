SELECT event_time, service_name, action_name, user_identity.email FROM system.access.audit WHERE event_date >= current_date() - 7 ORDER BY event_time DESC;
