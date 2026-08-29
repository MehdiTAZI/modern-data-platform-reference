# Identity and Governance

Human access is granted to account-level groups synchronized from the enterprise IdP. Workloads use service principals/managed identities. Azure Databricks Access Connector supplies storage/Event Hubs identity. Unity Catalog is the data authorization boundary.

```text
IdP -> Databricks account groups -> catalog/schema/table grants
GitHub OIDC/M2M -> deployment service principal -> Bundle deploy
Access Connector MI -> ADLS/Event Hubs
```

Production objects are group-owned; individual user ownership is not a target state.
