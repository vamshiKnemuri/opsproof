# Threat model

## Assets and trust boundaries

The protected assets are production clusters, the lab's availability, operational auditability, and the integrity of the evidence report. The model and log text are untrusted. The typed parser and deterministic policy are the authorization boundary. The Kind context and lab namespace are the execution boundary. A GitOps patch crosses to production only after separate human review.

| Threat | Control | Residual limitation |
|---|---|---|
| Prompt injection in app logs or runbooks | Treat text as data; parser rejects non-allowlisted kinds; policy requires cited Kubernetes status rather than a crash phrase in logs | A real model may still produce a bad but schema-valid proposal; no general robustness claim |
| Model emits shell or YAML | Extra-field rejection and fixed command mapping | A bug in the executor would still matter; review/tests remain necessary |
| Scope confusion or context drift | Dedicated `kind-opsproof` context, pinned namespace/deployment, no production context in policy | A malicious local kubectl binary or altered Kind context is outside this lab's guarantee |
| Disruptive scale or resource change | Minimum one replica, maximum three, delta at most one, fixed memory values and ceiling | One replica can still have downtime during rollout |
| False recovery claim | Readiness check, before/after measurement, rollback and reapply | Readiness is a narrow health proxy; no end-to-end SLO check |
| Secret leakage in Git | `.gitignore` excludes credentials and generated private reports | Users must still review patches and logs before committing |
| Ungated benchmark causes harm | Comparator runs solely in in-memory simulation | Results are fixture behavior, not real attack rates |

The evaluator does not grant an agent shell, kubeconfig, or direct API access. The optional model API sees evidence text and returns a proposal only. Human approval is required to carry the generated patch into a production GitOps repository.
