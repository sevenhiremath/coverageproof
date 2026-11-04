# Corrected owned Nikto integration — November 4, 2026

Source: `fix/browser-summary-check`, exact requested commit
`6d55609d8053821c2b86b7945bc5814ed71c23f3`.
Fresh worktree, notes branch `local/corrected-nikto-proof`. Existing checkout was
clean; earlier branches, failed recording and private bundles were preserved.
Read DELIVERY_PLAN.md, REQUIREMENTS.md, recording script and prior Nikto notes.
No merge, main change, model call, scanner retry or application edit occurred.

## Tests and containment

Existing Python 3.14.4 environment, this worktree on PYTHONPATH. Full pytest:
**131 passed, 1 warning in 10.73s**, exit 0. Whole captured command 14.4699431s.
Warning: existing upstream Starlette/httpx deprecation. This does not establish
the pending full Chromium visual verification.

Docker client/server 29.9.2 responded. Fixture source and Dockerfile matched the
previous built image sources. A no-target preflight and Nikto version check passed.
The recording's actual fixture was additionally inspected and probed **before
the script's first HTTP request**, with exact fixture source hash verified inside
the container. Assertions were added only in a private verification wrapper; the
recording script and all existing assertions remained unchanged.

Verified: fixture UID 10001; tool image user nikto and actual UID 100; only lo and
no external IPv4 routes; CapEff zero, NoNewPrivs 1 and Seccomp 2; fixture network
none, scanner shares only its namespace. No privileged mode, host binds/socket,
published ports or external Docker network. Root filesystems read-only; tool has
bounded tmpfs scratch. Limits: 1 GiB memory, 2 CPUs, 256 PIDs each. Saved actual
fixture/tool inspections and probes accompany the evidence. This is a dedicated
owned development namespace, not host services or organizer authorization.

## One corrected recording and verified import

Nikto **2.6.1 (LW 2.5)**, official image:
`ghcr.io/sullo/nikto@sha256:f65dd97be358e8260d97a00e784c05c5f37d2ed69b9a9611b14d3889c2b54efa`.
Only target: `http://127.0.0.1:8765/` in the owned fixture namespace.
Fixed literal tool command:

```text
/opt/nikto/nikto.pl -h http://127.0.0.1:8765/ -Tuning 1 -maxtime 60 -timeout 3 -nointeractive -nocheck -ask no -Format json -output /tmp/results.json
```

Ran scripts/record_owned_web.py once, tool nikto, fresh output/nikto-corrected.
The correction retrieved exact native JSON through docker exec cat, not the
archive-copy API. No export bytes were edited or reconstructed.

- Tool exit **0**; recording exit **0**; status **import_verified**.
- Start: 2026-11-04 11:42:01.510969 UTC (17:12:01.510969 IST).
- End: 11:42:07.995240 UTC (17:12:07.995240 IST).
- Recording wall time: **6.484274 seconds**.
- Native JSON: **1705 bytes**, SHA256
  `47e311a5d2fa3a1649aed40504ac355b9693b874d633c33e36381fcb2eaffc4d`.
- Parsing: **6 receipts**. Store import succeeded; database raw artifact bytes
  and stored hash match the native export exactly, mode **import**.
- Root check: finding_supported, 6 matching observations. Admin: unattempted,
  no matching observations. No unmatched receipts or app execution approvals.
- No condition_not_observed state was inferred from the alert export.
- Tool stderr empty; no submission prompt or update-check failure in stdout.

One normalized finding candidate contains five distinct source details under
`nikto:013587`. All five source observations remain preserved. Online product work
should review whether the generic Nikto plugin ID overgroups different header
conditions; integration success does not establish correlation correctness.

The script removed its two containers in finally; the separate preflight was
also removed. No unrelated Docker resources were changed.

## Evidence and remaining blocker

Private bundle includes unmodified raw JSON/stdout/stderr, native manifest with
literal Docker command/image digest/exit status, import.sqlite, imported snapshot,
independent import verification, actual containment inspections/probes, preflight
commands/version, source hashes, tests, recording timing/log and archive hashes.
Only sanitized notes are pushed. No key was loaded or displayed.

**Nikto checkpoint complete. ZAP has not run and remains the next integration
proof blocker.** No ZAP process, Groq call or Ollama start was performed. Full
browser/PDF verification remains separate online/local product work. Review the
genuine imported source grouping before making technical-accuracy claims; no
parser or correlation fix was attempted here.
