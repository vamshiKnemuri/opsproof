# Initial credential-free real-model trial

The two files in this directory came from the `local-model-evidence` artifact of [private GitHub Actions run #1](https://github.com/vamshiKnemuri/opsproof/actions/runs/36102041928), commit `ba4793eae406b4455f46a3363a139a0718258d57`, on 2026-09-25. The model was `qwen2.5:0.5b` on Ollama 0.34.4. The benchmark used three repeats of each of four synthetic incidents.

The guarded real-model row recovered 0/12; all 12 outputs were rejected by the typed parser or policy. There were no simulated side effects and no rollback attempts because no proposed action was allowed. The 512-token output cap truncated several responses. The fixed runbook and ungated fixture comparator in the same JSON are scripted controls, not real-model results. No Kind cluster was involved in this model trial.
