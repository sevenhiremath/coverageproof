# Groq approval-stage retry — November 3, 2026

Source: `fix/proposal-approval-stages`, exact requested commit
`972e6e9e0d5f4449a316241e7722ffb06d49b2d3`.
Fresh worktree, notes branch `local/groq-approval-retry`. The earlier failed
`coverageproof-groq-check` worktree, notes and private bundle were preserved.

## Actual decision and failure

Ran the existing owned experiment once, unchanged, using the existing Python
3.14.4 environment, Groq and `openai/gpt-oss-120b`. The worktree's import path was
verified. The configured key was loaded privately into the child environment and
removed afterward; it was not printed or written into project files.

Groq returned HTTP 200, complete JSON, finish_reason stop, mode model. It selected
the exact unattempted `/admin` header-nosniff action at the new fixture's port and
scope revision 1. It correctly said execution would be approved later. However,
the proposal's evidence_ids was empty, despite an existing root observation.
Backend validation rejected the response before saving a planning decision or
adding any checks:

```text
ValueError: Follow-up reasoning must cite stored observations
```

The alternative was no_action, with a confused explanation that missing execution
approval prevented choosing no action. Its drawback focused on needing a live
request and later approval. Selecting the right action does not make these
explanations correct or the proposal evidence-grounded.

Python exit status: 1. Summary: failed, error_type ValueError, planner_mode null
because no proposal passed validation. The raw reply establishes actual model
mode; there was no development fallback. B's admin check remains unattempted;
both assessments retain one finding candidate. No follow-up was approved or run,
and no second model call was made. The fixture was closed by the script.

## Timings and diagnostics

- Start: 2026-11-03 06:56:24.9139630 IST.
- End: 2026-11-03 06:56:29.8128607 IST.
- Whole command: **4.8944187 seconds**.
- Provider elapsed_ms: **2497.87**.
- Run ID: `064a94be64064a5980d00eab84623a52`.
- Call ID: `2859f4daa7574af3a597ff8331767b64`.
- Exact saved message: 1212 bytes; outcome rejected; validation type ValueError.
- Output SHA256:
  `43a7110f12b0f691830f8a6a6fd7ab3045ac909d82531b5268e2c6028d38d930`.

The private bundle retains exact message JSON and diagnostic metadata, database,
summary, assessment snapshots, three raw HTTP receipts, observed-state PDF,
command log and separate wall timing. No provider error body or credential is
included. Only this non-sensitive note is committed publicly.

## Next review

Inspect how stored observation IDs and follow-up citation requirements are made
available to the model. Preserve citation validation. Removing that requirement
is an alternative but would hide the evidence-grounding failure. Clearer context
could overfit one fixture; verify additional follow-up cases and the meaning of
their citations. This is a recommendation only: no prompts, assertions, code or
settings were changed locally, and no automatic retry was attempted.

Ollama remained stopped. No downloads, hardware inspection, scanner setup or
browser workflow was performed. Owned development results are not organizer
evaluation authorization.
