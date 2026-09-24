"""Deterministic authorization independent of any model output."""
from dataclasses import dataclass

from .models import Action, Evidence


@dataclass(frozen=True)
class PolicyContext:
    namespace: str = "opsproof-lab"
    deployment: str = "opsproof-app"
    current_replicas: int = 1
    current_memory_mib: int = 128
    previous_revision_available: bool = True
    service_min_replicas: int = 1
    max_replica_delta: int = 1
    max_memory_mib: int = 256
    allowed_memory_mib: tuple[int, ...] = (64, 128, 256)
    production: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "reasons": list(self.reasons)}


def evaluate(action: Action, evidence: Evidence, context: PolicyContext) -> PolicyDecision:
    reasons: list[str] = []
    if context.production:
        reasons.append("production execution is prohibited")
    if (action.namespace, action.deployment) != (context.namespace, context.deployment):
        reasons.append("action is outside the isolated deployment scope")
    if (evidence.namespace, evidence.deployment) != (context.namespace, context.deployment):
        reasons.append("evidence scope does not match policy scope")
    unknown = set(action.evidence_ids) - evidence.ids()
    if unknown:
        reasons.append(f"unknown evidence ids: {sorted(unknown)}")
    if len(action.reason.strip()) < 12:
        reasons.append("reason must explain the evidence-backed change")
    cited = [o for o in evidence.observations if o.id in action.evidence_ids]
    by_source = {o.source: o for o in cited}
    if action.kind == "deployment_rollback":
        if not context.previous_revision_available:
            reasons.append("no prior deployment revision exists")
        if not by_source.get("history", None) or not by_source["history"].data.get("previous_revision_available"):
            reasons.append("rollback requires cited prior-revision evidence")
        event_reason = by_source.get("events").data.get("reason") if "events" in by_source else None
        log_reason = by_source.get("logs").data.get("reason") if "logs" in by_source else None
        if event_reason not in ("ImagePullBackOff", "CrashLoopBackOff") and log_reason != "crash":
            reasons.append("rollback requires cited rollout failure evidence")
    elif action.kind == "set_replicas":
        target = action.target_replicas
        assert target is not None
        if "health" not in by_source or "available_replicas" not in by_source["health"].data:
            reasons.append("replica adjustment requires cited readiness evidence")
        if target < context.service_min_replicas or target > 3:
            reasons.append("replica target violates service availability or maximum")
        if abs(target - context.current_replicas) > context.max_replica_delta:
            reasons.append("replica change exceeds disruption bound")
    elif action.kind == "set_memory_limit":
        target = action.memory_mib
        assert target is not None
        if target not in context.allowed_memory_mib or target > context.max_memory_mib:
            reasons.append("memory limit is outside allowed values")
        if target > max(64, context.current_memory_mib * 4):
            reasons.append("memory increase exceeds fourfold bound")
        if "events" not in by_source or by_source["events"].data.get("reason") != "OOMKilled":
            reasons.append("memory adjustment requires cited OOMKilled event")
        if "metrics" not in by_source or by_source["metrics"].data.get("memory_limit_mib") != context.current_memory_mib:
            reasons.append("memory adjustment requires cited current limit")
    return PolicyDecision(not reasons, tuple(reasons) if reasons else ("allowed in isolated lab scope",))
