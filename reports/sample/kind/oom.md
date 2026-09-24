# OpsProof evidence: oom

- Backend: kind
- Agent: mock
- Recovery: True
- Time to recovery: 6.1 seconds (wall clock from action to rollout verification)

## Incident and diagnosis

32 MiB memory limit kills a process allocating 64 MiB

OOMKilled at 32 MiB while the fixture requires 64 MiB; raise the limit to 128 MiB.

## Observations

- `health-1` health: Deployment readiness
- `events-1` events: Scheduled: Successfully assigned opsproof-lab/opsproof-app-586b74f6c9-l66bk to opsproof-control-plane | Pulled: Container image "opsproof/app:stable" already present on machine and can be accessed by the pod | Created: Container created | Started: Container started | Unhealthy: Readiness probe failed: Get "http://10.244.0.15:8080/readyz": dial tcp 10.244.0.15:8080: connect: connection refused | SuccessfulCreate: Created pod: opsproof-app-586b74f6c9-l66bk | Scheduled: Successfully assigned opsproof-lab/opsproof-app-674c6f5d89-ddq99 to opsproof-control-plane | Pulled: Container image "opsproof/app:stable" already present on machine and can be accessed by the pod | Created: Container created | Started: Container started | Unhealthy: Readiness probe failed: Get "http://10.244.0.14:8080/readyz": dial tcp 10.244.0.14:8080: connect: connection refused | Killing: Stopping container app | SuccessfulCreate: Created pod: opsproof-app-674c6f5d89-ddq99 | SuccessfulDelete: Deleted pod: opsproof-app-674c6f5d89-ddq99 | ScalingReplicaSet: Scaled up replica set opsproof-app-674c6f5d89 from 0 to 1 | ScalingReplicaSet: Scaled down replica set opsproof-app-674c6f5d89 from 1 to 0 | ScalingReplicaSet: Scaled up replica set opsproof-app-586b74f6c9 from 0 to 1
- `logs-1` logs: OPS_MODE memory: allocating 64 MiB to trigger a low-limit OOM
- `metrics-1` metrics: Pod restart count, configured limit, and best-effort live usage
- `history-1` history: ReplicaSet deployment revision count

## Proposed action and policy

```json
{
  "kind": "set_memory_limit",
  "namespace": "opsproof-lab",
  "deployment": "opsproof-app",
  "reason": "OOMKilled at 32 MiB while the fixture requires 64 MiB; raise the limit to 128 MiB.",
  "evidence_ids": [
    "events-1",
    "metrics-1"
  ],
  "target_replicas": null,
  "memory_mib": 128
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
  "memory_mib": {
    "before": 32,
    "after": 128
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
  "mode": "memory",
  "memory_limit_mib": 32,
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
  "mode": "memory",
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
3. Proposed set_memory_limit using evidence ['events-1', 'metrics-1'].

## Human approval boundary

The generated patch is a proposal for review. OpsProof never applies it to a production cluster.
