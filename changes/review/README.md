# OOM remediation review proposal

This patch proposes a bounded memory-limit change from 32 MiB to 128 MiB for the isolated `opsproof-lab/opsproof-app` fixture. It came from the deterministic simulation rehearsal in `reports/sample/oom.json`. That rehearsal reported recovery and a successful rollback test under the simulation oracle.

The authoring environment did not have Docker, Kind, or kubectl, so this proposal has **not** been validated against a real cluster. Run `python -m opsproof scenario oom --backend kind` and inspect its generated report before considering this patch for any GitOps workflow. The patch is scoped to the lab namespace and must not be applied to production as-is. A human must approve any adapted production change.
