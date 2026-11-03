# Windows evidence bytes and candidate experiment — November 4, 2026

Source: `fix/recorded-evidence-bytes`, exact requested commit
`c58958eb3f118282abfdbb372e89dbd26d760b97`.
Fresh worktree and notes branch `local/evidence-bytes-check`. All earlier failed
runs and evidence were preserved. Existing Python 3.14.4 environment was reused.

## Gates

Recorded nmap.xml working-copy SHA256 now equals its manifest exactly:
`6c96a1bc3ce04d0474aecc3747ada86a767bb1dc5c6a702443a2ea0a35773877`.
No manual byte conversion, assertion change or Git setting change was made.

Tests: **131 passed, 1 warning in 12.57s**, exit 0. Whole test command including
capture: 13.7407171 seconds. The warning is upstream Starlette/httpx deprecation.
Dry evaluation: **completed**, 12 cases, baseline **10/12**, zero model calls.
The changed candidate-v2 regression suite is not the older 40db03b live batch.
No live evaluation batch was run.

## Single owned Groq experiment

Unchanged experiment ran exactly once with `COVERAGEPROOF_PROVIDER=groq`,
`GROQ_MODEL=openai/gpt-oss-120b` and the existing private key, using the existing
Python environment with this worktree on PYTHONPATH. No fallback or retry.

Result: **completed**, model mode, exit **0**. The actual model selected candidate
`0c31980860694e3da24a386127ba9c3d` with typed basis
`{"kind":"check","id":"0c31980860694e3da24a386127ba9c3d"}`.
The adapter resolved that ID to the exact stored admin header-nosniff action.
The saved planning decision has `contract_version=candidate-v2`. Empty legacy
observation citations are appropriate here: the typed basis is the unattempted
declared check, not fabricated observations for that target.

The explanation identified the admin check as unanswered and policy-allowed.
After planning, the script recorded exact approval and executed the bounded
follow-up. B's admin state changed from unattempted to condition_not_observed;
the root remained finding_supported. Initial counts were [1,1] and both remain
one finding candidate. B contains two consumed approvals (initial root and later
admin follow-up). Four genuine HTTP artifacts and the exact model reply were
independently hash-checked. The fixture was shut down by the experiment.

Explanation limitations: the abstain alternative says no other candidate exists;
this does not fully explain why abstaining is unsuitable. The drawback honestly
states no prior target observations and unknown results pending execution, but
does not describe the narrow one-response coverage limit. A single eligible
candidate does not establish multi-candidate prioritization or general AI quality.
The recorded negative is limited to the nosniff condition on that response.

## Timings and private diagnostics

- Start: 2026-11-04 04:36:51.1862470 IST.
- End: 2026-11-04 04:37:04.1032305 IST.
- Whole experiment: **12.9134202 seconds**.
- Saved provider elapsed_ms: **10626.661**.
- HTTP 200, finish_reason stop, complete reply, 932 bytes, outcome accepted.
- Run ID: `e530f39c237047e5a439a037cac26306`.
- Model call: `481b65e30a734f7c9245f02c23f008d6`.
- Exact output SHA256:
  `c2a693aa84fa6021ff112ebc2c39ef19e24696b06118ea06c04d328b3d6112dd`.

Private bundle includes fixture hash verification, test log/timing, dry suite and
results, exact model JSON/trace, experiment database and snapshots, summary,
HTTP evidence, generated PDFs, command timing/log and exact-byte hash manifest.
No credential or raw diagnostic is committed. Key absence in output files was
checked before packaging. Only these non-sensitive notes are published.

Next, assess several eligible candidates and abstention with a freshly frozen
suite after quota review. Repeating this fixture is an alternative but tests less
generalization. Broader evaluation costs calls and requires independent expected
choices and semantic review; keep eligibility, scope and approvals enforced.
This is a recommendation only, not another scheduled run.

No local code/prompt/settings changes, downloads, scanner runs or Ollama use.
Owned development evidence does not establish organizer evaluation authorization.
