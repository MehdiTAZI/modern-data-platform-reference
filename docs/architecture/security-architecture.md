# Security Architecture

## Principles

1. Authenticate workloads with workload/service identities rather than personal credentials.
2. Grant access to groups, not individual users, wherever possible.
3. Separate platform administration from data ownership.
4. Isolate environments and sensitive domains at governance boundaries appropriate to risk.
5. Prefer short-lived credentials and managed identity mechanisms.
6. Log administrative and data-access events.

## Authorization model

```text
Identity Provider
   -> Groups / Service Principals
      -> Unity Catalog grants
         -> Catalog
            -> Schema
               -> Tables / Views / Volumes
```

Production objects should be owned by controlled groups or service principals. Application identities receive the minimum privileges necessary for their deployment and runtime responsibilities.

## Secrets

Secrets must never be committed to the repository. Terraform variables containing credentials should be injected by CI/CD or backed by an external secret manager. Application code should resolve secrets through platform-supported secret references or workload identity.
