# Changelog

## 0.1.0 — 2026-09-29

Initial portfolio release of the executable DevOps incident lab.

- Docker/Kind fixtures for bad images, application crashes, OOM kills, and prompt injection.
- Read-only evidence collection, a deterministic mock agent, and optional Ollama/OpenAI adapters.
- Strict typed actions with scope, evidence, and disruption checks before lab execution.
- Recovery, side-effect, fault-recurrence, and rollback checks before generating a review patch.
- Comparable repeated simulator trials, separate historical real-model evidence, sample reports, and CI.
- Architecture, threat model, setup commands, and a two-minute demo script.

The reviewed code passed 24 tests and all four Kind scenarios in [CI run #24](https://github.com/vamshiKnemuri/opsproof/actions/runs/36170672414). Mock and real-model results remain distinct. The optional OpenAI adapter has stubbed tests but no live API trial. This release evaluates a single-deployment lab with readiness as its health proxy; it has no production execution adapter.
