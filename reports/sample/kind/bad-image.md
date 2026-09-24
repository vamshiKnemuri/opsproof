# OpsProof evidence: bad-image

- Backend: kind
- Agent: mock
- Recovery: True
- Time to recovery: 3.66 seconds (wall clock from action to rollout verification)

## Incident and diagnosis

deployment references an image absent from the cluster

ImagePullBackOff began after a bad image revision; restore the prior revision.

## Observations

- `health-1` health: Deployment readiness
- `events-1` events: Scheduled: Successfully assigned opsproof-lab/opsproof-app-66456749bb-lxntv to opsproof-control-plane | Pulling: Pulling image "opsproof/app:missing" | Failed: Failed to pull image "opsproof/app:missing": failed to pull and unpack image "docker.io/opsproof/app:missing": failed to resolve reference "docker.io/opsproof/app:missing": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed | Failed: Error: ErrImagePull | SuccessfulCreate: Created pod: opsproof-app-66456749bb-lxntv | Scheduled: Successfully assigned opsproof-lab/opsproof-app-674c6f5d89-5d4rl to opsproof-control-plane | Pulled: Container image "opsproof/app:stable" already present on machine and can be accessed by the pod | Created: Container created | Started: Container started | Killing: Stopping container app | SuccessfulCreate: Created pod: opsproof-app-674c6f5d89-5d4rl | SuccessfulDelete: Deleted pod: opsproof-app-674c6f5d89-5d4rl | ScalingReplicaSet: Scaled up replica set opsproof-app-674c6f5d89 from 0 to 1 | ScalingReplicaSet: Scaled down replica set opsproof-app-674c6f5d89 from 1 to 0 | ScalingReplicaSet: Scaled up replica set opsproof-app-66456749bb from 0 to 1
- `logs-1` logs: 
- `metrics-1` metrics: Pod restart count, configured limit, and best-effort live usage
- `history-1` history: ReplicaSet deployment revision count

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
  "image": {
    "before": "opsproof/app:missing",
    "after": "opsproof/app:stable"
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
  "restart_count": 0,
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
2. Proposed deployment_rollback using evidence ['events-1', 'history-1'].

## Human approval boundary

The generated patch is a proposal for review. OpsProof never applies it to a production cluster.
