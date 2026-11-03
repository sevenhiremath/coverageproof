# First live Groq result — November 3, 2026

Source: `feature/groq-provider`, requested commit
`5c4f51912bfd34dc510d7bd23c14b8dcc08500d8`.
Fresh worktree and notes branch `local/groq-check`; existing work preserved.

## Actual result

Ran `scripts/experiment.py` exactly once using the existing Python 3.14.4 venv,
this worktree on PYTHONPATH, provider `groq`, model `openai/gpt-oss-120b` and the
configured user-level key loaded privately into the child process environment.
No key was printed, embedded in a command, stored in project files or committed.
The process environment copy was removed after the run. Ollama stayed stopped.
No downloads, scanner execution or application changes were made.

Groq returned **HTTP 200**, complete output, finish_reason `stop`, `mode=model`
and **checks=[]**. It explained that the pending admin check needed new execution
approval and therefore no further check could be proposed. This confuses proposing
an action with permission to execute it. A proposal grants no approval; the owned
experiment grants exact approval only after the correct gap has been selected.

The JSON/schema was accepted and a real `planning_decision` was saved, but the
useful-gap experiment failed with Python exit **1**:

```text
AssertionError: Planner did not select the declared admin gap; preserve its decision and investigate
```

No action was substituted and no follow-up was approved or executed. A's states
remain `finding_supported`, `condition_not_observed`; B's remain
`finding_supported`, `unattempted`. Each assessment retains one finding candidate.
The three initial genuine HTTP receipts and the finally-exported failure state
are retained. The fixture shut down normally. No second model request was made.

## Timings

- Start: 2026-11-03 06:45:06.1908497 IST.
- End: 2026-11-03 06:45:09.7276246 IST.
- Whole command: **3.5324828 seconds**.
- Saved provider elapsed_ms: **1321.25**.
- Model output: 391 bytes; provider/schema outcome `accepted` means structured
  output acceptance, not successful experiment reasoning.

## Private diagnostics

Run: `cdc1c6d1ebce4b9992226950609189be`.
Call: `52eba9f272414f8b8e0d3cddedd483e2`.
Exact output SHA256:
`81eabf7d02438174d3cb11f295a4edd05d0b4ca4d0c9585a0d4338970afbcdbd`.

Private bundle: database, experiment summary, actual model message JSON and
metadata, assessment snapshots, raw HTTP receipts, observed-state PDF, command
log, separate wall timing and hash manifest. Credentials and provider error
bodies are not included. The summary correctly says failed, planner_mode model,
error_type AssertionError. No raw model prose or database is published in Git.

## Next review

Online Work should evaluate clarifying proposal-versus-execution approval in the
context, preserving the exact-gap assertion. This addresses the observed mistake.
Increasing timeout is an alternative but does not address a fast completed wrong
decision. Clarification can overfit one fixture; verify on held-out approved and
not-yet-approved candidate scenarios. No prompt change or extra run was made here.
One live call establishes endpoint/account access for this model at this time,
not reliable planning quality, report drafting quality or guaranteed future quota.
