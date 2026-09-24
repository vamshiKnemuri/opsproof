"""Human-readable evidence and reviewable GitOps-style patch artifacts."""
import json
from pathlib import Path
from typing import Any


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def change_patch(report: dict[str, Any]) -> dict[str, Any] | None:
    action = report.get("proposed_action", {})
    if report.get("policy_decision", {}).get("allowed") is not True:
        return None
    kind = action.get("kind")
    after = report["after"]
    spec: dict[str, Any] = {}
    if kind == "set_replicas":
        spec["replicas"] = after["desired_replicas"]
    elif kind in ("deployment_rollback", "set_memory_limit"):
        container: dict[str, Any] = {"name": "app"}
        if kind == "deployment_rollback":
            container["image"] = after["image"]
            container["env"] = [{"name": "OPS_MODE", "value": after["mode"]}]
        if kind == "set_memory_limit" or "memory_limit_mib" in report.get("change_diff", {}):
            container["resources"] = {"limits": {"memory": f"{after['memory_limit_mib']}Mi"}}
        spec["template"] = {"spec": {"containers": [container]}}
    else:
        return None
    return {"apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": action["deployment"], "namespace": action["namespace"]}, "spec": spec}


def write_report(outdir: Path, report: dict[str, Any], stem: str) -> tuple[Path, Path | None]:
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / f"{stem}.json"
    md_path = outdir / f"{stem}.md"
    write_json(json_path, report)
    lines = [f"# OpsProof evidence: {report['incident']}", "",
             f"- Backend: {report.get('backend', 'simulation')}",
             f"- Agent: {report.get('agent_type', report.get('approach', 'mock'))}",
             f"- Recovery: {report['recovery']}",
             f"- Time to recovery: {report['time_to_recovery_seconds']} seconds ({report['time_basis']})", "",
             "## Incident and diagnosis", "", report.get("cause_fixture", "See fixture in incidents.py."), "",
             report["diagnosis"], "", "## Observations", ""]
    for observation in report["evidence"]["observations"]:
        lines.append(f"- `{observation['id']}` {observation['source']}: {observation['summary']}")
    lines += ["", "## Proposed action and policy", "", "```json",
              json.dumps(report["proposed_action"], indent=2), "```", "", "```json",
              json.dumps(report["policy_decision"], indent=2), "```", "", "## Change diff", "", "```json",
              json.dumps(report["change_diff"], indent=2), "```", "", "## Measurements", "", "Before:", "", "```json",
              json.dumps(report["before"], indent=2), "```", "", "After:", "", "```json",
              json.dumps(report["after"], indent=2), "```", "", "## Side effects and rollback", "",
              f"Side effects: {report['side_effects']}", "", "```json",
              json.dumps(report["rollback"], indent=2), "```", "", "## Agent trace", ""]
    lines.extend(f"{index}. {step}" for index, step in enumerate(report["agent_trace"], 1))
    lines += ["", "## Human approval boundary", "",
              "The generated patch is a proposal for review. OpsProof never applies it to a production cluster.", ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    patch = change_patch(report)
    patch_path = None
    if patch:
        patch_path = outdir / f"{stem}-gitops-patch.json"
        write_json(patch_path, patch)
    return md_path, patch_path
