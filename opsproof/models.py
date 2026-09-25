"""Strict, transport-independent action and evidence models."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


class ValidationError(ValueError):
    pass


ActionKind = Literal["deployment_rollback", "set_replicas", "set_memory_limit"]


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    namespace: str
    deployment: str
    reason: str
    evidence_ids: tuple[str, ...]
    target_replicas: int | None = None
    memory_mib: int | None = None

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> "Action":
        if not isinstance(raw, dict):
            raise ValidationError("action must be an object")
        allowed = {"kind", "namespace", "deployment", "reason", "evidence_ids", "target_replicas", "memory_mib"}
        extra = set(raw) - allowed
        if extra:
            raise ValidationError(f"unknown action fields: {sorted(extra)}")
        required = {"kind", "namespace", "deployment", "reason", "evidence_ids"}
        missing = required - set(raw)
        if missing:
            raise ValidationError(f"missing action fields: {sorted(missing)}")
        kind = raw["kind"]
        if kind not in ("deployment_rollback", "set_replicas", "set_memory_limit"):
            raise ValidationError("action kind is not allowlisted")
        for key in ("namespace", "deployment", "reason"):
            if not isinstance(raw[key], str) or not raw[key].strip():
                raise ValidationError(f"{key} must be a nonempty string")
        ids = raw["evidence_ids"]
        if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x for x in ids):
            raise ValidationError("evidence_ids must be a nonempty string list")
        if len(set(ids)) != len(ids):
            raise ValidationError("evidence_ids must be unique")
        replicas = raw.get("target_replicas")
        memory = raw.get("memory_mib")
        if kind == "set_replicas":
            if type(replicas) is not int or "memory_mib" in raw:
                raise ValidationError("set_replicas requires only integer target_replicas")
        elif kind == "set_memory_limit":
            if type(memory) is not int or "target_replicas" in raw:
                raise ValidationError("set_memory_limit requires only integer memory_mib")
        elif "target_replicas" in raw or "memory_mib" in raw:
            raise ValidationError("rollback takes no numeric parameter")
        return cls(kind, raw["namespace"], raw["deployment"], raw["reason"], tuple(ids), replicas, memory)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["evidence_ids"] = list(self.evidence_ids)
        if self.kind != "set_replicas":
            value.pop("target_replicas")
        if self.kind != "set_memory_limit":
            value.pop("memory_mib")
        return value


@dataclass(frozen=True)
class Observation:
    id: str
    source: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Evidence:
    incident: str
    namespace: str
    deployment: str
    observations: list[Observation]
    untrusted_text: list[str] = field(default_factory=list)

    def ids(self) -> set[str]:
        return {o.id for o in self.observations}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Decision:
    diagnosis: str
    action: Action
    trace: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"diagnosis": self.diagnosis, "action": self.action.to_dict(), "trace": list(self.trace)}
