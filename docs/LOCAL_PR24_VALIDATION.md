# PR 24 local verification — November 5, 2026

Exact source: `a8d74d4cc0eaedf47590a67cfb4eee5ad254d77b`, fetched from PR 24.
Fresh worktree/notes branch `local/handoff-report-validation`. Previous evidence
and branches preserved. Verification only: no code/assertion edits, scans,
Groq/model calls, Ollama or main merges.

## Full test suite: failed

Existing Python 3.14.4 environment, this worktree on PYTHONPATH. One suite run:
**137 passed, 1 failed, 1 warning in 19.69s**. Do not describe this exact source
as locally all-green. Existing warning: upstream Starlette/httpx deprecation.

Failure: `tests/test_correlation.py:118`,
`test_context_is_displayed_in_ui_pdf_and_model_input`. The assertion requires
both `lab_only` and literal `Source severity first` in PDF text. The report now
uses readable ranking fields and does not print the latter literal phrase.
The test expectation and revised presentation need reconciliation online; no
assertion was removed, changed or rerun locally.

## Independent browser verification: passed

Ran unchanged scripts/check_browser.py with the previously installed private
Playwright 1.64.1 adapter and installed Chrome **156.0.8078.74**. No new package
or browser download. Fresh browser database and contexts, owned app/HTTP fixture
only, development planning and explicitly labelled synthetic report provider.
No model calls. Browser assertions remained unchanged.

Passed root/admin gap accounting, exact approvals and execution, evidence hash
download, synthetic draft exclusion before acceptance and after invalidation,
out-of-scope denial, no page errors and mobile no-horizontal-overflow assertion.
Visually reviewed desktop/mobile screenshots and downloaded report renderings:
no visible clipping or unusable controls in these captured states. New backend
operation, current-scope verdict and coverage limits are visible in the proposal
panel and wrap on mobile. Host-loopback development evidence does not establish
organizer-isolation compliance.

## Saved genuine Nikto report: passed core content checks

SQLite backup of the accepted replay assessment; original evidence untouched.
Generated through the app's supported report.pdf route. No reimport or new scan.
All seven rendered pages inspected. Verified five distinct candidates, five
`method GET` entries, unknown severity, unassessed exploitability and admin still
unattempted. Plain-HTTP HSTS applicability wording explicitly avoids an inference
about HTTPS policy or an exploitable weakness. Risk fields are readable lines;
hash is in the separate Evidence manifest. Finding sections stay together without
visible clipping. Output SHA256:
`1ce6ce5b3f57f294c71c489d9042cdc985b58e64fd9e5245c1c12706a00847e5`.

The layout now uses seven pages versus the earlier six, with more whitespace.
This is a tradeoff for keeping full findings together, not lost content.

## Remaining defects and reproductions

1. Run pytest on this exact source: the literal PDF ranking-string assertion above
   fails. Review expected wording without weakening the risk-context contract.
2. Open the browser-generated HTTP report, detailed finding page: it prints
   `http | method unknown` while the same source detail contains `GET`. The new
   Nikto method display works, but live HTTP receipts/presentation should also
   identify the actual supported runner method consistently. No fix made here.
3. Each browser PDF spans five pages, with only the final tail of an audit event
   on page five. Open accepted-test-draft.pdf page 5 to reproduce. Audit remains
   raw JSON and can create nearly empty trailing pages. No text is clipped.
4. The saved Nikto assessment has no proposal decision, but still shows an empty
   Proposal action facts section and scope-verdict explanatory line. Minor polish:
   distinguish no proposals from an evaluated scope verdict.

Private evidence bundle:
`C:\Users\seven\Downloads\CoverageProof_Checkpoint_1\CoverageProof-pr24-validation-evidence.zip`.
Includes actual failure log, browser summary/screenshots/downloads, fresh report
and copied assessment DB, text/renderings, verification data and hashes. Only
these sanitized notes are public. ZAP proof remains separately unfinished; no
scanner or provider task was added to this local verification.
