# Local model and report check — November 2, 2026

Source: main commit `6831839718da963293e22380013d5558a5ce3890`.
Branch: `local/model-browser-checks`. Fresh GitHub clone; older extractions preserved.
No application code, policy, prompts or model settings were changed.

## Actual model run

Python 3.14.4 venv; editable `.[test]` installation succeeded. Ollama's local
version endpoint reported 0.40.11. Its installed-model endpoint listed
`qwen3.5:9b`, digest
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
No model download, paid API or subscription automation was used.

Run the existing experiment with these PowerShell settings:

```powershell
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:PYTHONPATH='.'
.\.venv\Scripts\python scripts/experiment.py
```

Actual start: 2026-11-02 22:05:20.5027941 IST.
Actual end: 2026-11-02 22:08:07.9313759 IST.
Whole-command wall time: 167.4190567 seconds; Python exit status: 1.
This includes fixture setup and initial HTTP checks, not just model inference.
The last initial evidence timestamp to planning failure spans about 164.2 seconds;
the provider does not separately save exact inference duration.

The real response failed Pydantic validation:

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for Proposal
checks.0.action
  Value error, Unknown registered check [type=value_error, input_value={'check': 'no_additional_...n', 'scope_revision': 1}, input_type=dict]
```

That input excerpt is exactly the truncated diagnostic printed by Pydantic.
The provider did not save the complete rejected model JSON. Do not reconstruct
or claim a full proposal from that excerpt. No valid planning decision was saved.
The database contains `planning_failed` with provider `ollama`, no added checks
and no fallback. The experiment stopped before its admin follow-up assertion and
execution. No prompt adjustment or substitute development run was attempted.

The three genuine initial HTTP receipts were preserved and their SHA256 values
matched the stored artifact hashes. Assessment A has one finding candidate and
states `finding_supported`, `condition_not_observed`. B also has one candidate,
with states `finding_supported`, `unattempted`. No B admin approval/execution
occurred. This is owned host-loopback development evidence, not isolated scanner
evaluation or organizer authorization. The ephemeral fixture was shut down by
the experiment's finally block; old targets were not reexecuted.

## Browser access blocker

The installed stable Tabbit launcher failed on both `create` and `diagnose`:

```text
CLI_REGISTRATION_UNAVAILABLE
Tabbit CLI registration refers to unavailable browser components or user data,
possibly after an upgrade. Restart the current Tabbit Browser to refresh
registration, then retry.
```

The user chose to continue and report this blocker rather than restart Tabbit.
No browser version, UI screenshot or real browser walkthrough was obtained.
No browser repair, alternate automation backend or browser install was attempted.

The app did start on 127.0.0.1:8000 with the saved experiment database. `/health`
returned provider `ollama` and scanner execution `disabled`. The B assessment
page returned HTTP 200 with coverage, audit and report-draft controls. These are
HTTP checks only, not browser verification. No report-draft button was clicked,
no model report prose was accepted, and stale-draft exclusion after adding a
check remains unverified locally. No separate live browser fixture was started.

## PDF inspection

Generated `observed-state-vapt.pdf` from B's real saved failure state, exported
raw HTTP artifacts/snapshots, and downloaded another PDF through the app route.
The experiment's normal success-only `experiment-summary.json` and
`sample-vapt.pdf` were not produced; `validation-summary.json` is explicitly a
failure-state export, not a replacement successful experiment result.

Both inspected PDFs contain three pages, preserve the unattempted admin check,
show the planning failure, and say there is no current analyst-accepted AI draft.
Bounded negative wording does not claim the asset is secure. The generated report
was rendered with installed Poppler at 1400 pixels and all three PNGs visually
inspected: no visible clipping, overlap or missing text; page three has substantial
blank space. The renderer emitted these warnings despite producing readable pages:

```text
Syntax Error: No display font for 'Symbol'
Syntax Error: No display font for 'ArialUnicode'
```

Resolved dependencies include FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.2,
httpx 0.28.1, ReportLab 4.5.1 and pypdf 6.21.4. The full dependency list and private
evidence stay in the local bundle. Existing online test claims were not counted
as fresh local test results for this commit.

## Smallest next steps

1. Online Work should inspect this genuine registered-action failure and add
   diagnostics that preserve rejected structured output safely. This solves the
   missing full-response evidence. Increasing timeout is an alternative, but this
   call returned a validation error before timeout. More logging has a privacy
   drawback, so store bounded output privately. Verify with the same experiment
   and retain any failure; do not weaken its declared-gap assertion.
2. Restart Tabbit normally, then repeat the specified browser/report-draft review
   and staleness checks. This restores real UI verification. HTTP-only checks are
   an alternative, but cannot verify layout or clicking behavior. Restarting may
   interrupt browser work; save it first. Verify the stable launcher connects and
   record actual screenshots, browser version and model-call timings.

No hardware inspection, scanner setup, scanner execution, Docker network change,
model download or application redesign was performed. Only this concise note is
intended for public Git; the database, logs, PDFs and raw evidence stay private.
