# Local model retry — November 2, 2026

Source: `bcbc3ebc6378f2091f5c97f7c085d8172a277535` (current main at fetch).
Notes branch: `local/model-retry`, in a separate worktree. Older checkout and
`local/model-browser-checks` were preserved.

## Actual result: valid output, wrong next check

The existing `scripts/experiment.py` exited **1**, with:

```text
AssertionError: Planner did not select the declared admin gap; preserve its decision and investigate
```

Ollama returned HTTP 200, complete JSON, `mode=model`, and `done_reason=stop`.
The app accepted the structured proposal and saved a `planning_decision`.
This is not a successful experiment: schema acceptance does not establish useful
or accurate reasoning.

The model proposed `header-nosniff` for the already-assessed root URL, citing its
real observation. Its reason was that `/admin` supposedly fell outside
`allowed_paths=["/"]`. It supplied `no_action` as the alternative and described
inability to assess admin paths as its drawback. That scope interpretation is
wrong: domain.py's path-boundary rule treats `/` as the root subtree. A read-only
`validate_scope` call using the saved scope and saved admin action succeeded.
The proposal also says no additional check is needed while still proposing the
completed root check. No prompt, schema, policy or model option was changed to
correct these errors locally.

The admin follow-up was not approved or executed. Both assessments retain one
finding candidate. A's states are `finding_supported`, `condition_not_observed`;
B's are `finding_supported`, `unattempted`. Three genuine initial HTTP artifacts
were exported. The fixture was closed by the script's finally block. These are
owned loopback development results, not organizer-authorized scanner evaluation.

The failure summary has `status=failed`, `error_type=AssertionError` and
`planner_mode=null`, because the script sets planner_mode only on success. The
saved planning event and exact reply independently establish actual model mode;
the null summary must not be interpreted as development mode.

## Timings and runtime

- Start: 2026-11-02 23:12:23.0323883 IST.
- End: 2026-11-02 23:14:49.3806277 IST.
- Whole command: **146.341639 seconds**, including fixture and export work.
- Provider `elapsed_ms`: **144314.689**.
- Ollama reported total duration: 144.1444066 seconds; load: 15.0897321 seconds;
  prompt evaluation: 32.9504 seconds; generation: 96.05072 seconds.
- Prompt tokens: 1717; generated tokens: 753.
- Python 3.14.4; Ollama 0.40.11; existing `qwen3.5:9b`.
- Installed model digest:
  `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.

To honour the explicit no-download instruction, this worktree reused the prior
installed venv instead of creating another one and installing dependencies.
`PYTHONPATH=.` and an import-location check confirmed this worktree's source was
loaded. Exact command, from the retry worktree:

```powershell
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:PYTHONPATH='.'
..\coverageproof-current\.venv\Scripts\python scripts/experiment.py
```

## Private diagnostics and evidence

Run ID: `738fff3f456f4848b40b8f5fc17b4b4f`.
Call ID: `4f39fb1795bd4c82acab81b5328d0175`.
The saved diagnostic contains exact model message JSON (1043 bytes), complete
and untruncated, plus timing/token/hash metadata. Its `outcome=accepted` refers
to provider/schema validation, not the useful-gap assertion.

Exact message SHA256:
`8153df7dbe6b86395e1cfc296e15421ba99604c4f558a80b5b115ed41606875a`.
The raw output hash and all three HTTP artifact hashes were independently checked
against the saved manifests/snapshots. Database, failed experiment summary,
current assessment JSON, raw HTTP, observed-state PDF, command log, wall timing
and recursive model diagnostics are retained in the private evidence bundle.
No raw model prose or database is committed publicly.

## Next step for online review

Use this failure to clarify the path-boundary semantics in the model context and
evaluate a fresh exact-gap run, while preserving the assertion. This addresses
the observed reasoning error. Increasing timeout is an alternative, but the
response completed before timeout and was semantically wrong. More explicit
context can overfit this example; verify on additional allowed/excluded-path
cases rather than treating one success as broad accuracy. This is a recommendation
only; no prompts or application source were changed here.

No hardware checks, browser repair, scanner setup/execution, model downloads or
new tests were performed. Browser/PDF workflow was not repeated during this
model-only retry. PR merges and web-scan approval remain outside this run.
