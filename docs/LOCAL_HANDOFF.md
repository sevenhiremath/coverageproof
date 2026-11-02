# Paste this task into the local ChatGPT app

Continue CoverageProof from https://github.com/sevenhiremath/coverageproof . Online Work owns the app and is using GitHub Actions for Docker validation. Backend tests and a genuine isolated Nmap recording/import have passed online. Official Nikto/ZAP images, versions and help were inspected online; web target execution awaits exact approval in docs/WEB_CHECK_PLAN.md. Do not repeat capability inspection, build another scanner lab, change Docker networks, tune hardware or download another AI model.

Your local task is only actual Ollama reasoning and browser/PDF verification, which require the model and desktop already installed on this machine. Read README.md, docs/STATUS.md and docs/DECISIONS.md. Preserve the old extraction. Use the current main commit after PR #2 is merged, or the exact tested feature commit supplied by online Work.

## Get the source in a fresh folder

```powershell
git clone https://github.com/sevenhiremath/coverageproof.git coverageproof-current
cd coverageproof-current
git switch -c local/model-browser-checks
git status --short
git rev-parse HEAD
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e '.[test]'
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:PYTHONPATH='.'
.\.venv\Scripts\python scripts/experiment.py
```

Use the already-installed qwen3.5:9b model, no paid API key or subscription automation. Python 3.14 was reported installed; if dependency setup fails, return the exact error rather than replacing system Python. Start the existing Ollama service normally if needed; do not download models or change hardware settings. Never dump environment variables or credentials.

The experiment creates its own benign loopback HTTP fixture and two assessments with equal initial issue counts. With the environment above, planning must be actual model mode. It now asserts that the model selected the declared admin gap before running the approved follow-up. If the model returns the wrong check, invalid citations, a timeout or malformed JSON, preserve that real failure and the database; do not weaken the check or substitute development mode. Return actual wall-clock duration, model/runtime versions and the saved proposal/error. These host-loopback results are owned development evidence, not isolated scanner evaluation or organizer authorization.

## Browser and report walkthrough

Start the same durable experiment database:

```powershell
$env:COVERAGEPROOF_DB='output/experiment.sqlite'
.\.venv\Scripts\python -m uvicorn coverageproof.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 in a real browser. Inspect the newly created assessments, model decision, alternative, drawback, real observation IDs, approval audit and bounded negative wording. The experiment's ephemeral fixture has stopped, so do not reexecute its old target or assume it is reachable. Do not import GitHub loopback scanner evidence into a host-loopback scope: these are different fixture environments despite the same address.

For report drafting, use the saved experiment evidence: click the report-draft button, record the actual Ollama result, inspect each check/evidence citation, accept only accurate statements with a reason and download the PDF. Verify no unreviewed or stale prose appears. Add a new explicit declared check to invalidate the accepted draft, then confirm the PDF excludes it. Record real browser/version, elapsed model-call times and PDF page/layout issues.

For a separate live browser follow-up, start `local-lab/fixture.py` in another terminal with the venv Python. Create a NEW self-owned development assessment for literal 127.0.0.1/32, port 8765, allowed paths / and /admin, exclusions empty and an explicit owned-fixture authorization reference. Approve exact header-nosniff actions in the app before executing. No unrelated host services or native scanner commands. Preserve evidence and errors; do not invent results. A fixture missing nosniff is one response-header condition, not a general app vulnerability conclusion.

## Return precisely this

1. Current source commit, actual model/runtime/browser versions and the genuine model proposals/errors with elapsed times.
2. Browser/PDF checks performed, failures and non-sensitive screenshots.
3. Privately return output/experiment.sqlite, experiment-summary.json, the generated PDF and raw .http evidence. Do not publicly commit the whole database or private user data. Public sample selection happens after inspection.
4. Commit only concise reproducible validation notes under docs/ on local/model-browser-checks, using a plain message such as 'Record the local model and browser check'. Push normally, no force push or source redesign. Return the branch/commit and evidence bundle.

Stop only on a concrete runtime/access blocker and report the exact command/error. Do not return another machine capability report. No organizer messages, invitations, final submission or public Drive links.
