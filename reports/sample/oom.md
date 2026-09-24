# OpsProof evidence: oom

- Backend: simulation
- Agent: mock
- Recovery: True
- Time to recovery: 10 seconds (deterministic simulation clock: 5s action + 5s verification)

## Incident and diagnosis

32 MiB memory limit kills a process allocating 64 MiB

OOMKilled at 32 MiB while the fixture requires 64 MiB; raise the limit to 128 MiB.

## Observations

- `health-1` health: Readiness probe has zero available replicas
- `events-1` events: Pod reports OOMKilled
- `logs-1` logs: Memory allocator started
- `metrics-1` metrics: Memory limit and restart signal
- `history-1` history: A healthy prior revision is available

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
  "available_replicas": {
    "before": 0,
    "after": 1
  },
  "memory_limit_mib": {
    "before": 32,
    "after": 128
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
  "image": "opsproof/app:stable",
  "mode": "memory",
  "memory_limit_mib": 32,
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
  "mode": "memory",
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
2. Proposed set_memory_limit using evidence ['events-1', 'metrics-1'].

## Human approval boundary

The generated patch is a proposal for review. OpsProof never applies it to a production cluster.
