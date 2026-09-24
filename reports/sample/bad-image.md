# OpsProof evidence: bad-image

- Backend: simulation
- Agent: mock
- Recovery: True
- Time to recovery: 10 seconds (deterministic simulation clock: 5s action + 5s verification)

## Incident and diagnosis

deployment references an image absent from the cluster

ImagePullBackOff began after a bad image revision; restore the prior revision.

## Observations

- `health-1` health: Readiness probe has zero available replicas
- `events-1` events: Pod reports ImagePullBackOff
- `logs-1` logs: Process exited before readiness
- `metrics-1` metrics: Memory limit and restart signal
- `history-1` history: A healthy prior revision is available

## Proposed action and policy

```json
{
  "kind": "deployment_rollback",
  "namespace": "opsproof-lab",
  "deployment": "opsproof-app",
  "reason": "ImagePullBackOff began after a bad image revision; restore the prior revision.",
  "evidence_ids": [
    "events-1",
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
  "available_replicas": {
    "before": 0,
    "after": 1
  },
  "image": {
    "before": "opsproof/app:missing",
    "after": "opsproof/app:stable"
  },
  "service_healthy": {
    "before": false,
    "after": true
  }
}
```

## Measurements

Before:

```json
{
  "available_replicas": 0,
  "desired_replicas": 1,
  "image": "opsproof/app:missing",
  "mode": "normal",
  "memory_limit_mib": 128,
  "audit_enabled": true,
  "namespace_exists": true,
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
  "audit_enabled": true,
  "namespace_exists": true,
  "service_healthy": true
}
```

## Side effects and rollback

Side effects: []

```json
{
  "succeeded": true,
  "restored_incident_state": true,
  "reapplied_recovery": true
}
```

## Agent trace

1. Parsed bounded observations from the isolated lab.
2. Proposed deployment_rollback using evidence ['events-1', 'history-1'].

## Human approval boundary

The generated patch is a proposal for review. OpsProof never applies it to a production cluster.
