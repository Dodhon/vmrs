# Neo4j CI/CD Research (VMRS)

Objective: capture Neo4j CI/CD practices and references relevant to a HITL knowledge-graph backend, with emphasis on backups, migrations, testing, and Docker/Kubernetes deployment.

## Sources (official)
- APOC Core docs: https://neo4j.com/docs/apoc/current/
- Operations Manual – Docker (overview): https://neo4j.com/docs/operations-manual/current/docker/
- Operations Manual – Dump/Load (Docker): https://neo4j.com/docs/operations-manual/current/docker/dump-load/
- Operations Manual – Backup/Restore (index): https://neo4j.com/docs/operations-manual/current/backup-restore/
- Operations Manual – Consistency checker: https://neo4j.com/docs/operations-manual/current/backup-restore/consistency-checker/
- Operations Manual – Kubernetes backup/restore (Helm chart): https://neo4j.com/docs/operations-manual/current/kubernetes/operations/backup-restore/
- Upgrade & Migration Guide (Neo4j 5): https://neo4j.com/docs/upgrade-migration-guide/current/version-5/migration/migrate-databases/

## Sources (community/tools)
- Neo4j-Migrations (docs): https://michael-simons.github.io/neo4j-migrations/current/
- Neo4j-Migrations (repo): https://github.com/michael-simons/neo4j-migrations
- Testcontainers (Neo4j module): https://java.testcontainers.org/modules/databases/neo4j/
- Liquigraph (archived): https://github.com/liquibase/liquigraph
- Neo4j Kubernetes Operator backup/restore examples: https://github.com/neo4j-partners/neo4j-kubernetes-operator/tree/main/examples/backup-restore

---

## 1) Core CI/CD building blocks (official guidance)
### Docker operations
The Docker operations chapter covers:
- Docker Compose setups and clustering.
- Plugin loading (APOC).
- Docker-specific `neo4j-admin` / `cypher-shell` operations.
- Offline dump/load and online backup/restore (Enterprise).

### Backup/restore + validation
The Operations Manual is the canonical reference for:
- Backup planning and modes (online/offline).
- Restore procedures.
- Consistency validation using `neo4j-admin database check` (offline validation of DB, dump, or backup artifacts).

### Kubernetes (Helm chart)
The K8s operations docs describe:
- Online backups via in-cluster Admin Service.
- Full + differential backup chains to cloud storage (S3/GCS/Azure).
- Backup job configuration using Helm values and workload identity.

### Version upgrades
The Upgrade/Migration guide highlights:
- Neo4j 5 Java requirements (Java 17; Java 21 supported from 5.14+).
- Running dual versions for upgrades requires resource/port separation.

---

## 2) CI/CD pipeline pattern (distilled)
### CI (build + test)
1. Provision Neo4j (Docker or Testcontainers).
2. Install APOC (version pinned to Neo4j runtime).
3. Seed data deterministically (Cypher/APOC or dump/load).
4. Run integration tests (cover HITL workflows).
5. Optional: `neo4j-admin database check` on dump/backup artifacts.

### CD (deploy + migrate)
1. Create backup (online or offline).
2. Apply migrations (Cypher or migration tooling).
3. Validate (consistency check + smoke tests).
4. Deploy (pin Neo4j/APOC/Java versions).
5. Rollback via restore (dump or backup chain).

---

## 3) Community tooling highlights
### Neo4j-Migrations (Flyway-style)
- CLI + API to apply versioned Cypher migrations.
- Tracks applied migrations as a subgraph in Neo4j.
- Useful in CI/CD or app startup for schema + seed data.

### Testcontainers
- Spin up Neo4j for integration tests (Bolt or HTTP endpoints).
- Supports Neo4j 5.x images and custom plugins (APOC).

### Liquigraph (archived)
- Previously common migration tool; repo is read-only as of May 2025.

---

## 4) HITL-specific considerations
- Store HITL decisions as append-only events (auditability).
- Maintain draft vs approved graph views (labels/props).
- Use deterministic “promotion” step (Cypher/APOC refactor) for approved data.
- Persist provenance (source, annotator, timestamp).

---

## 5) Concrete commands (official docs)
### Docker offline dump
```
docker run --interactive --tty --rm \
  --volume=$HOME/neo4j/data:/data \
  --volume=$HOME/neo4j/backups:/backups \
  neo4j/neo4j-admin:2025.12.1 \
  neo4j-admin database dump neo4j --to-path=/backups
```

### Docker offline load
```
docker run --interactive --tty --rm \
  --volume=$HOME/neo4j/newdata:/data \
  --volume=$HOME/neo4j/backups:/backups \
  neo4j/neo4j-admin:2025.12.1 \
  neo4j-admin database load neo4j --from-path=/backups
```

### Consistency check
```
neo4j-admin database check <database>
```

---

## Recommendation
Use Testcontainers + deterministic seed data for CI, and enforce backup + migration + consistency checks in CD. Pin Neo4j/APOC/Java versions to avoid upgrade drift.

## Next steps
Confirm CI system and deploy target for VMRS (GitHub Actions vs other; Docker vs K8s). I can draft a concrete pipeline YAML and a migration/rollback runbook tailored to the HITL workflow.
