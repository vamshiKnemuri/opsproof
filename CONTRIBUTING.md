# Contributing to OpsProof

Work from a source checkout with Python 3.10 or newer. The offline path uses only the standard library. Docker, Kind, and kubectl are needed for cluster rehearsals.

## Verify a change

From the repository root:

```sh
python -m unittest discover -s tests -v
python -m opsproof attack-check
python -m opsproof demo --backend simulation --out reports/generated
```

For changes to fixtures, evidence collection, the policy, or the Kind executor, also run:

```sh
python -m opsproof setup
python -m opsproof demo --backend kind --out reports/generated
```

The CI workflow runs both paths. A failure to recover must remain a failed result; a blocked or unsuccessful proposal must not produce a GitOps patch.

## Preserve the safety boundary

- Add actions through the strict parser, deterministic policy, and fixed argument mapping together.
- Keep logs and runbooks as untrusted evidence. They cannot authorize an action.
- Keep all execution pinned to the disposable lab. Production review happens outside this project.
- Run unsafe comparator behavior only in the in-memory simulation.
- Cover concrete risks with regression tests, including blocked actions and unsuccessful rollback.

## Report results honestly

Keep mock-agent, real-model, and Kind results separate. Include the source commit or workflow run, model identity when applicable, trial count, failures, and timing basis. Simulator recovery time excludes inference latency and must be labeled simulated. Preserve historical evidence rather than editing its numbers to match newer code.

Generated reports belong under `reports/generated/` unless deliberately reviewed and added as synthetic sample evidence. Do not commit credentials, kubeconfigs, personal documents, or real operational logs. Model API credentials stay in the local environment; never include them in an issue or pull request.
