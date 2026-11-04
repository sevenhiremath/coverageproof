# Local consolidated proof — November 4, 2026

Exact source: `a0e0e002cf07f1144f08f80ecf4ce46a5c41a9e7`
(`test/store-planner-cases`). Fresh worktree/notes branch `local/consolidated-proof`.
Accepted 134 tests and genuine Nikto replay were not repeated. No relevant app
code/dependencies were changed. Previous evidence and worktrees are intact.

| Task | Status | Observed result |
|---|---|---|
| ZAP preparation | Passed | One bounded official-image pull completed in 24.54 seconds |
| ZAP recording/import | Failed | One baseline invocation, tool exit 3; no JSON; import not reached |
| Browser workflow | Passed | Existing script/assertions, Chrome 156, desktop/mobile and three downloaded PDFs reviewed |
| Analyst handoff | Passed core state checks, defects below | Five distinct conservative claims, admin unanswered, fresh six-page PDF |

Private evidence bundle:
`C:\Users\seven\Downloads\CoverageProof_Checkpoint_1\CoverageProof-consolidated-proof-evidence.zip`.
Raw logs, databases, images and PDFs are private. Only these sanitized notes are
published. No Groq/model calls, Ollama, main merge or unrelated resource change.

## 1. ZAP preparation and failed recording

Initial Docker image/cache inspection found no usable ZAP image. Prior cancelled
pull logs showed completed downloads for many layers, but no final image digest.
They do not establish whether the prior stall was registry access, transfer speed,
extraction or another cause. Do not infer a causal diagnosis from silence.

Read-only space checks: C: free 90,038,460,416 bytes; total 509,522,997,248.
Docker fixture overlay free 976,166,285,312 bytes. Docker reported build cache
27.94 GB and image storage 17.51 GB. No cleanup or cached-layer removal occurred.
These checks do not establish space availability in every bounded tmpfs.

Exactly one new `docker pull ghcr.io/zaproxy/zaproxy:stable` was authorized and
performed. A private wrapper enforced a 600-second hard limit and cancellation
after 180 seconds without observable output progress. It completed in
24.537577 seconds, exit 0, reusing cached layers. No second pull or alternate image.
Actual official digest:
`sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af`.

Same owned fixture containment was verified, including the actual fixture before
its first HTTP request: only lo, no external routes, non-root, no effective
capabilities, no-new-privileges, read-only root, no host mounts/socket/published
ports. The tool shares the fixture's network-none namespace with bounded tmpfs,
1 GiB memory, 2 CPUs and 256 PIDs. All evidence is saved privately.

No-target version probe reported **ZAP 2.17.0 / Java 17.0.21**, exit 0. However,
subsequent review of its retained stderr found **No space left on device** during
add-on installation. Its .ZAP tmpfs is 128 MiB. It also reported an unresolved
container hostname, and chose -Xmx3934m despite the 1-GiB container limit. These
are actual diagnostics, not proof of an OOM or the exact baseline failure cause.
The private preflight wrapper treated exit 0 as readiness and did not gate on
these logged errors; that readiness check was insufficient. Containment checks
did pass. No source/assertion was weakened.

Existing scripts/record_owned_web.py ran **once**, tool zap, fresh
output/zap-recording. Literal baseline command:

```text
zap-baseline.py -t http://127.0.0.1:8765/ -m 1 -T 2 -J /tmp/results.json --autooff
```

Start 2026-11-04 13:48:48.942763 UTC (19:18:48.942763 IST); end 13:48:53.902553
UTC. Recording duration **4.959806 seconds**. Baseline exit **3** (error), recording
exit **1**. Actual retained tool diagnostic: `Failed to start ZAP :(`. Export
retrieval: `cat: /tmp/results.json: No such file or directory`. Scratch listing
contained only exit-status. No native JSON, parsing, import database or negative
coverage was produced. Missing alerts are not interpreted as a clean result.
The baseline's underlying startup cause is not proven beyond that message;
version-probe scratch/memory diagnostics identify concrete issues for review.
No retry or resource/configuration repair was attempted. Task containers removed.

## 2. Independent real-browser workflow

Reviewed scripts/check_browser.py and Dockerfile.browser. No compatible Python
Playwright package or downloaded browser cache existed in the prior venv, and no
browser Docker image was present. Installed Chrome was available. A first attempt
to match bundled Node Playwright 1.62.1 failed because that Python version was not
published. Then the Dockerfile's declared Python Playwright **1.64.1** was installed
only under output/browser-python-deps, leaving the app environment unchanged.
No Chromium or large image download. The setup logs are retained.

A private launch adapter supplied installed Chrome's executable to the existing
script. All workflow assertions remained unchanged. Fresh database:
output/browser-fresh.sqlite. Chromium contexts were fresh and headless, visiting
only the owned loopback app/fixture; this is host development verification, not
organizer-isolation proof. Planning was **development**, report provider a
**labelled synthetic test provider**. No real model service was called.

Browser **156.0.8078.74**, workflow **passed**, wall time **9.227639 seconds**:

- Correct root/admin gap counts before and after exact approvals/execution.
- Finding count remains one while admin becomes condition_not_observed.
- Browser evidence download matches stored SHA256.
- Synthetic draft excluded before acceptance, included after acceptance, excluded
  after adding unassessed check. All three PDFs downloaded through the UI.
- Out-of-scope target denied without issuing its target request.
- Final states finding_supported, condition_not_observed, unattempted.
- No page errors; mobile 390x844 overflow assertion passed.

Visually reviewed desktop/mobile screenshots and all 12 rendered pages of the
three four-page PDFs. No visible text clipping, horizontal overflow or unusable
controls in the captured states. PDF synthetic wording is explicitly labelled
automated test, not live AI. States and accepted/stale prose match the assessment.
Minor limits: dense JSON audit text, some long findings split across page breaks.

## 3. Genuine analyst handoff

Copied the existing accepted replay database with SQLite backup; did not reimport
or rescan evidence. Requested the fresh report through the app's supported
`GET /assessments/{id}/report.pdf` route using TestClient, status 200. Original DB
unchanged. Rendered and inspected all **six pages** and checked its saved state:

- Five source-reported header candidates remain distinct.
- All severities unknown; CVSS None; exploitability not_assessed.
- HSTS on the HTTP target is labelled tool-reported, source_reported, suspected
  and analyst-review-required. Remediation says confirm applicability. No claimed
  exploitability or independently established impact. Specific HTTP/HSTS context
  is absent (defect below), but generic conservative framing is present.
- Admin remains unattempted; summary says one unanswered declared check.
- Artifact SHA256, observation IDs and native source pointers are retained.
- No accepted AI draft is included; scope/coverage/evidence limits are explicit.

## Defects and reproduction

1. **ZAP readiness/error diagnostics (integration blocker).** On this commit use
   the saved official image and literal recording command above. The no-target
   version probe exits 0 while .ZAP add-on writes log no space; baseline logs
   failed startup and exits 3 without an export. Do not rerun automatically.
   Inspect the private preflight stderr and bounded scratch/JVM configuration;
   ensure readiness verifies usable startup, not only version exit status, before
   authorizing another recording. Preserve startup logs before container cleanup.
2. **Nikto PDF omits preserved HTTP method (handoff defect).** Generate a report
   from the accepted five-candidate replay. Native/Store observations preserve GET,
   but PDF source entries print tool/outcome/time/message without method; extracted
   report text contains no GET. Show the method beside the URL/source pointer so
   readers can interpret method-sensitive grouping. No fix made here.
3. **Generic HSTS applicability explanation (clarity defect).** In analyst PDF
   page 4, strict-transport-security is reported for http://127.0.0.1:8765/ with
   generic applicability/impact caveats. It does not specifically explain the
   plain-HTTP context or what further validation is needed. Retain the genuine
   scanner claim, but make its applicability uncertainty explicit before client
   remediation decisions; do not upgrade it to a proved exploitable vulnerability.
4. **Dense report/fragmented finding (usability defect).** Five simple header
   claims take six pages with long grouping hashes and raw risk dictionaries.
   Referrer-policy starts on page 3 and its source/limitations continue on page 4
   without repeating the finding title. No clipping was observed, but this weakens
   quick handoff. Compare pages 3–4 and the risk JSON under each candidate.

Online work can review these concrete defects independently. Existing immutable
evidence must remain intact. Any ZAP configuration change needs a new reviewed
bounded run; this batch schedules no further run or provider call.
