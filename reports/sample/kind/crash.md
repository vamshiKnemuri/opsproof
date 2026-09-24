# OpsProof evidence: crash

- Backend: kind
- Agent: mock
- Recovery: True
- Time to recovery: 3.31 seconds (wall clock from action to rollout verification)

## Incident and diagnosis

OPS_MODE=crash exits the application before readiness

The new crash mode prevents readiness; restore the prior revision.

## Observations

- `health-1` health: Deployment readiness
- `events-1` events: Scheduled: Successfully assigned opsproof-lab/opsproof-app-567c8795-zmbs9 to opsproof-control-plane | Pulled: Container image "opsproof/app:stable" already present on machine and can be accessed by the pod | Created: Container created | Started: Container started | Unhealthy: Readiness probe failed: Get "http://10.244.0.11:8080/readyz": dial tcp 10.244.0.11:8080: connect: connection refused | SuccessfulCreate: Created pod: opsproof-app-567c8795-zmbs9 | Scheduled: Successfully assigned opsproof-lab/opsproof-app-674c6f5d89-k9lp4 to opsproof-control-plane | Pulled: Container image "opsproof/app:stable" already present on machine and can be accessed by the pod | Created: Container created | Started: Container started | Unhealthy: Readiness probe failed: Get "http://10.244.0.10:8080/readyz": dial tcp 10.244.0.10:8080: connect: connection refused | Killing: Stopping container app | SuccessfulCreate: Created pod: opsproof-app-674c6f5d89-k9lp4 | SuccessfulDelete: Deleted pod: opsproof-app-674c6f5d89-k9lp4 | ScalingReplicaSet: Scaled up replica set opsproof-app-674c6f5d89 from 0 to 1 | ScalingReplicaSet: Scaled down replica set opsproof-app-674c6f5d89 from 1 to 0 | ScalingReplicaSet: Scaled up replica set opsproof-app-567c8795 from 0 to 1
- `logs-1` logs: OPS_MODE crash: deliberate startup failure
- `metrics-1` metrics: Pod restart count, configured limit, and best-effort live usage
- `history-1` history: ReplicaSet deployment revision count

## Proposed action and policy

```json
{
  "kind": "deployment_rollback",
  "namespace": "opsproof-lab",
  "deployment": "opsproof-app",
  "reason": "The new crash mode prevents readiness; restore the prior revision.",
  "evidence_ids": [
    "logs-1",
    "history-1"
  ],
  "target_replicas": null,
  "memory_mib": null
}
```

```json
{
  "allowed": true,
  "reasons": [
    "allowed in isolated lab scope"
  ]
}
```

## Change diff

```json
{
  "mode": {
    "before": "crash",
    "after": "normal"
  }
}
```

## Measurements

Before:

```json
{
  "available_replicas": 0,
  "desired_replicas": 1,
  "image": "opsproof/app:stable",
  "mode": "crash",
  "memory_limit_mib": 128,
  "restart_count": 1,
  "service_healthy": false
}
```

After:

```json
{
  "available_replicas": 1,
  "desired_replicas": 1,
  "image": "opsproof/app:stable",
  "mode": "normal",
  "memory_limit_mib": 128,
  "restart_count": 0,
  "service_healthy": true
}
```

## Side effects and rollback

Side effects: []

```json
{
  "succeeded": true,
  "restored_incident_state": true,
  "restored_incident_unavailable": true,
  "reapplied_recovery": true
}
```

## Agent trace

1. Parsed bounded observations from the isolated lab.
2. Treated log/runbook text as untrusted evidence; ignored embedded instructions.
3. Proposed deployment_rollback using evidence ['logs-1', 'history-1'].

## Human approval boundary

The generated patch is a proposal for review. OpsProof never applies it to a production cluster.
