# Security Architecture

Principles: least privilege; workload identities; short-lived CI credentials; no secrets in Git; separation of platform admin, data engineering and analyst roles; auditability; explicit network trust boundaries; encryption in transit/at rest; governed external storage through Unity Catalog.

The public reference leaves `public_network_access_enabled=true` for reproducibility while classic compute has `no_public_ip=true`. Organizations requiring private control-plane access should apply the documented Private Link/private DNS variant before production adoption.
