# Accepted Nikto replay — November 4, 2026

Source: exact requested commit `a0e0e002cf07f1144f08f80ecf4ce46a5c41a9e7`.
Fresh worktree/notes branch `local/nikto-grouping-replay`. Previous worktrees,
recordings and private bundles preserved. No application source was changed.

Full tests using the existing Python 3.14.4 environment: **134 passed, 1 warning
in 14.92s**. Warning: existing upstream Starlette/httpx TestClient deprecation.

Replayed only the accepted genuine native Nikto JSON from the corrected recording:
1705 bytes, SHA256
`47e311a5d2fa3a1649aed40504ac355b9693b874d633c33e36381fcb2eaffc4d`.
Verified that hash before import. A fresh local SQLite assessment declared the
same exact root/admin web-server checks and explicitly identified this operation
as offline replay of an owned isolated recording. No target service was contacted.

## Observed grouping and import

- Parser: **6 receipts** (one export limitation receipt plus five finding receipts).
- Store: **5 separate finding candidates**, each with one native source observation.
- Separate conditions: content-security-policy, x-content-type-options,
  permissions-policy, referrer-policy, strict-transport-security.
- Every source retains native class nikto:013587, exact message and source pointer.
- Every saved method is **GET**, matching the native artifact. This genuine sample
  contains no different-method example; broader method behavior is unit-tested.
- URL remains http://127.0.0.1:8765/ for all five observations.
- Root state finding_supported; admin unattempted, no observation invented.
- Database artifact bytes exactly equal the native file; hash and import mode match.
- No approvals, target requests, scanner runs or model calls.
- Replay wall time **1.207056 seconds**.

The earlier import grouped these five messages into one candidate. This replay
verifies the fix against that same unedited recording. Exact-message grouping
does not establish broader semantic equivalence or cross-tool correlation.

Private evidence: fresh replay database/snapshot, source JSON copy, per-condition
summary, test log and exact-byte hash manifest. Raw database/evidence stay private;
only this sanitized note is published. Existing accepted source evidence is intact.

No live AI evaluation or new six-case freeze was run. Genuine ZAP import proof
and final browser/report verification remain separate unfinished work. Ollama
was not started; no keys were loaded or displayed. No Docker cleanup occurred.
