# Local model retry — exact task

Online fix: model check names are now enum values in the schema, not unrestricted strings. The prompt includes the schema and explains that no-action is checks=[], not an invented action. Rejected JSON is saved privately with hashes, elapsed time and validation locations. This fix passed mocked regression tests; actual model success is not yet verified.

In the existing local checkout, preserve your notes branch and create a separate worktree from current main after the fix is merged:

```powershell
git status --short
git fetch origin
git worktree add -b local/model-retry ../coverageproof-model-retry origin/main
cd ../coverageproof-model-retry
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e '.[test]'
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:PYTHONPATH='.'
.\.venv\Scripts\python scripts/experiment.py
```

Use the existing model/runtime. No downloads, hardware tuning, browser repairs or scanner setup. This reruns only the same owned loopback development experiment already authorized. Do not reuse old ephemeral target addresses.

Expected success: summary status completed, planner_mode model, both initial issue counts 1, B's admin check changes from unattempted to condition_not_observed after the model selects that exact check and the fixture follow-up is approved. There must be a planning decision and a model-call timing record. This single success would not establish broad planning accuracy.

Expected failure handling: nonzero exit, summary status failed, current snapshots/HTTP evidence and observed-state-vapt.pdf still exported, no substituted follow-up. Do not rename checks, weaken assertions, change prompts or switch to development mode. A model returning checks=[] can be schema-valid yet fail the useful-gap experiment; keep that failure too.

Return privately: output/experiment.sqlite, experiment-summary.json, observed-state-vapt.pdf, current assessment JSON/.http evidence and output/model-diagnostics/<run_id>/ (exact model JSON plus metadata). The exporter does not print or publish raw replies. The old missing JSON cannot be reconstructed. Do not commit raw output or the database. Add only concise non-sensitive observed results to docs/ on local/model-retry and return its commit. Record whole-command wall time separately from the provider's saved elapsed_ms.

If your browser launcher is still blocked, leave it alone. Online Work is preparing isolated Chromium verification in GitHub Actions. Actual model prose/report review will follow once planning is working.
