# Actual planner scope retry — November 3, 2026

Source: `fix/planner-scope-context`, exact requested commit
`ac797d6247bc41d8c803dc5485975769c94b19f3`.
Fresh worktree, notes branch `local/planner-scope-retry`. Existing branches and
extractions preserved. Followed PLANNER_SCOPE_FIX.md and its model retry task.

## Result

Ran the existing experiment **once**. Exit status **0**, summary **completed**,
planner mode **model**. No prompts, settings, checks, assertions or application
source were changed locally, and no development fallback was used.

The actual model chose the exact unattempted `header-nosniff` action for `/admin`
at the experiment's newly assigned loopback port and scope revision 1. It correctly
described the endpoint as authorized and cited the real root-response observation.
Its rationale was to investigate the declared gap; it suggested root's missing
header pattern might extend to admin. Its alternative was no action, rejected
because it would skip verification. Its drawback warned that a single endpoint
check does not cover subpath variations.

The claimed root pattern was a hypothesis, not established admin evidence. The
actual approved follow-up observed nosniff on admin, so that condition became
`condition_not_observed`. This verifies the bounded check, not safety of admin or
other paths. The drawback wording is generic; useful explanation quality still
needs broader evaluation.

Both initial finding counts were 1. A initially had `finding_supported` and
`condition_not_observed`; B had `finding_supported` and `unattempted`. After the
model-selected, explicitly approved follow-up, B had `finding_supported` and
`condition_not_observed`, still with one finding candidate. B has two consumed
exact-action approvals. One genuine model planning decision and its timing record
are saved. Citations resolve to stored observations. Four genuine HTTP artifacts
and the exact model output were hash-checked successfully.

## Timing and runtime

- Whole command start: 2026-11-03 06:30:51.7212594 IST.
- Whole command end: 2026-11-03 06:33:19.4671230 IST.
- Whole-command wall time: **147.7357647 seconds**.
- Provider elapsed time: **142021.392 ms**.
- Ollama total duration: 141.4649826 seconds; load: 14.6939011 seconds;
  prompt evaluation: 37.097218 seconds; generation: 89.645573 seconds.
- Prompt tokens: 1944; generated tokens: 651.
- Python 3.14.4, existing prior venv; import path verified against this worktree.
- Ollama 0.40.11, existing `qwen3.5:9b`, digest
  `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.

Exact command, from this worktree (no dependency/model downloads):

```powershell
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:PYTHONPATH='.'
..\coverageproof-current\.venv\Scripts\python scripts/experiment.py
```

## Private evidence

Run ID `5a948e97fee645d481b82f690d9f3ce1`.
Call ID `4485a441641d40f3969f150affa1574c`.
Diagnostic: HTTP 200, complete response, done_reason stop, accepted; 746 bytes
of exact output JSON, no captured-response truncation.
Output SHA256:
`f8117c7d97eb2b05a52efbbfe3d2d240dc36434d64c3b679456c8ab4b0c91d2b`.

The private bundle includes experiment.sqlite, final experiment-summary.json,
assessment snapshots, four raw .http artifacts, observed-state-vapt.pdf and
sample-vapt.pdf, exact model output/diagnostic manifests, runtime versions,
command log, separate whole-command timing and a recursive hash manifest.
No raw response, database or evidence is published in Git.

## Limits and next evaluation

This one eligible-gap experiment succeeded. It does not establish general model
accuracy, multi-option selection, abstention, report prose quality or organizer
evaluation authorization. No browser/PDF walkthrough, hardware inspection,
scanner setup, scanner execution or new automated test run was performed here.

Next, evaluate held-out scopes with several eligible actions and abstention. This
tests meaningful choice beyond one eligible gap. Repeating this same fixture is
an alternative, but gives less evidence about generalization. Held-out evaluation
costs additional model time and needs independent expected outcomes; verify exact
allowed actions, citations and absence of execution without approval in each case.
This is a recommendation only; no additional model call was made.
