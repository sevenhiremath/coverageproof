# PS-1 compliance matrix

Authority: attached `PS -1(2).pdf` (10 pages) and `Rules DataOps Innovation Hackathon(2).pdf` (7 pages), read fully on 2026-11-02. Both research reports are byte-identical background documents. Their recommendation to remove AI planning is rejected: PS-1 §11 gives AI reasoning 20/100.

| Requirement | Exact page/section | Implementation component | Verification / current state |
|---|---|---|---|
| Conversational request, authorized scope, auditable plan | PS-1 p2 §3; p5 §6 | Request form, Scope, planner, decision events | Request stored; deterministic development plan tested; live model validation pending |
| Adaptive tool selection and explained next action | PS-1 p4 §5.2, p9 §11 | Registry + provider + schema/evidence validator | Development rules work; provider implemented, credentials and live AI evaluation pending |
| At least 3 working integrations/imports, network and web | PS-1 p3 §4; p5 §6 | Nmap XML, Nikto JSON, ZAP JSON adapters | Three parsers schema-tested; genuine outputs from owned lab still required before claiming verified integrations |
| Approved orchestration, timeout/error status | PS-1 p4 §5.3 | One-job HTTP runner, one-use approval, attempts | Live owned HTTP fixture verified; native scanner runners disabled |
| Normalization, duplicates and distinct assets | PS-1 p4 §5.4 | Receipts; findings grouped by exact canonical URL and issue class | Exact-asset grouping and explicit HTTP/ZAP 10021 mapping preserve all evidence; broader mapping awaits genuine scanner outputs |
| Tool/asset/time/raw refs/evidence/confidence/status | PS-1 p4 §5.5 | Hashed artifacts, observations, candidates | Tested; absent native fields remain null/unknown |
| Severity/CVSS/exposure/exploitability/impact/confidence | PS-1 p4 §5.6 | Source severity ordering, missing inputs visible | Source severity plus attributed exposure/impact/validation; confidence labels retained; missing CVSS stays unknown; contextual accuracy requires analyst review |
| Approval for offensive validation; audit outcomes | PS-1 p2 boundary; p4 §5.7; p7 §9.5 | Exact action + whole scope fingerprint, one-use approval | Binding/replay/denial tests pass; offensive scanner validation not yet implemented |
| Professional downloadable PDF, executive + technical | PS-1 p4 §5.8; pp5–6 §§7.1–7.6 | Immutable report snapshots + ReportLab | API/PDF text consistency tested; rendered sample visually checked |
| All-seven truthful integration matrix | PS-1 p5 §6; pp7–8 §9.6 | INTEGRATIONS.md | Maintained; unverified formats explicitly described |
| Working authorized-lab prototype + sample PDF + architecture/source/setup | PS-1 p7 §§9.1–9.4 | App, docs, sample script | Owned development evidence exists; organizer lab authorization not supplied |
| No public-system testing, no fabricated output, grounded AI | PS-1 p10 §13 | Literal IP scope, no redirects/proxies, no arbitrary commands | Policy tests; unit fixtures labeled synthetic; no scanner demo fabricated |
| Implemented versus planned functionality | Rules p2 §3.4–3.6 | STATUS.md, explicit UI labels | Core test suite and limitations documented |
| Licensed reuse + attribution + disclose prior work | Rules p2 §4; pp2–3 §5; p3 §7 | THIRD_PARTY.md | No copied upstream implementation; dependencies used under licenses |
| Required accessible submission links | Rules p3 §6; official portal Submission | SUBMISSION.md | No entry submitted; Drive links not yet created |

## Bonuses (not baseline replacements)
PS-1 p5 §6: multi-step adaptive memory, all-seven live/API support, confidence calibration, false-positive triage/remediation tracking, retesting/change comparison, exports, team workflows. Retesting is deferred.

## Product-specific checks
Explicit state vocabulary includes supported finding, condition not observed, inconclusive, failed, unattempted, not applicable, blocked, conflict and stale scope. Not-applicable classification requires an applicability receipt; no automatic service-down => not-applicable conversion. General helper supports not-applicable; user-facing adjudication is pending.

## Delivery targets (IST)
Nov 2: policy/store/import contracts and first workflow. Nov 3: genuine three-tool lab outputs and central experiment. Nov 4: live grounded model decisions, correlation and analyst review. Nov 5: full workflow/report/browser verification. Nov 6 evening: freeze candidate, record demo, prepare slides and check links. Nov 7: submission buffer; only user submits/authorizes final entry.

## Additional organizer instructions: November 2 meeting

Source is the user-supplied orientation transcript; it has no PDF page numbers. Full recorded constraints are in ORIENTATION_2026-11-02.md.

| Requirement | Exact section / statement in meeting | Implementation / delivery component | Verification |
|---|---|---|---|
| Tests and performance metrics in isolated environment | Opening rules: isolated testing must not affect other services/apps | Authorized isolated lab and containment record | Pending; online loopback development tests are not isolation proof |
| PS-selection and mentorship form by EOD | Mentorship instructions: team leader/individual completes form, strict EOD deadline | User form action Nov 2 IST | Not submitted by app/assistant |
| Mentorship optional, Nov 4–5 slots | Mentorship explanation and later clarification | Optional mentor review | Slot not known; recommend opt-in |
| Human-voiced screen recording, 1–3 minutes | Video Q&A: no AI voices; min 1, max 3 minutes | Demo script/recording, target 2:45 | Pending |
| Accessible Drive PPT/video and GitHub code, deadline Nov 7 11:59 PM IST | Submission explanation | Submission checklist | Links not yet published or submitted |
| Secure coding, smooth execution, clear explanation | Judging Q&A | Security review, reproducible setup, live-demo preparation | Partial backend tests; full review pending |
| Shortlist live presentation | Final-round explanation: top 10–20 teams | Live walkthrough/demo fallback | Future stage; no selection assumed |
| Support ticket for organizer queries | Closing support instructions | User-approved support ticket if needed | None sent |
