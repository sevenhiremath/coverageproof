# CoverageProof handoff — checkpoint 1, 2026-11-02

## Verified
- Read PS-1 and rules completely; exact section/page matrix in REQUIREMENTS.md. PS-2 inspected only as background; PS-1 is selected.
- 31 pytest tests pass, including a real loopback HTTP fixture and PDF/API consistency; synthetic scanner schema inputs and timeout injections are labeled tests, not genuine scanner evidence.
- Genuine two-assessment HTTP experiment: baseline issue counts [1,1]; A states [finding_supported, condition_not_observed]; B states [finding_supported, unattempted]. Approved targeted follow-up changes B to [finding_supported, condition_not_observed] while issue count stays 1.
- Sample PDF generated, rasterized and visually checked. Font fallback improved to DejaVu where available; no false clean claim.
- FastAPI server starts online. Host/Origin boundary and UI routes pass TestClient checks. Browser package exists, but Chromium absent; attempted browser download returned invalid/truncated ZIP. No browser verification claimed.
- Editable package setup tested after fixing explicit package discovery and template package-data.

## Pending / blockers
1. Source is published at public sevenhiremath/coverageproof. The initial GitHub checkpoint is 899104b; later changes use normal feature branches. Presentation/video access remains a pre-submission task.
2. No native scanners or Docker online. apt update fails with setgroups/seteuid permission errors. First minimal local Nmap task is in LOCAL_SCANNER_TASK.md. Three native parsers exist, but genuine scanner recording verification is incomplete.
3. Model providers implemented, not called live; the user has a local Ollama model but no paid API access. Use secret environment variables, never chat or source code. Development mode explicitly rule-based. Do not call the finished project an intelligent agent until real planning decisions are validated.
4. Organizer-authorized evaluation lab access/scope not supplied. Self-owned fixtures only establish development behavior.
5. Native isolated scanner execution, per-path exclusions, imported-age staleness, cross-tool issue mapping, contextual risk enrichment and report narrative drafting need implementation.
6. Browser verification, Docker image build and full named-tool end-to-end demonstration remain unverified.

## Next increment
Push the tested checkpoint once repository exists. Obtain genuine Nmap XML, Nikto multi-host JSON and ZAP traditional JSON from owned lab; add regression fixtures with provenance. Close genuine-format mismatches. Then enable schema-validated model planning with evidence citations and implement analyst review. Preserve the baseline and do not spend time on bonus retest/team features.

## Environment
Python dependencies install; no GPU/containers assumed. SQLite and local HTTP sockets work. Raw data and runtime outputs excluded from accidental commits except explicitly selected public self-owned samples. Server binds loopback; no internet deployment or final submission performed.

## Orientation update recorded November 2
See ORIENTATION_2026-11-02.md. Next work must enforce isolated-lab evaluation, security-review/readiness checks, 1–3 minute human-voiced demo and accessible Drive links. The user must complete the PS-selection/mentorship form by EOD today (IST); mentorship remains optional. No form/ticket has been submitted. Current loopback checks remain development evidence, not proof of isolated evaluation compliance.

## Next increment: understandable decisions and local handoff
Each proposed check now records a relevant alternative, why it was not selected and a drawback of the chosen action. The workspace displays these summaries; live model proposals missing them are rejected. Deterministic development explanations remain labeled as such. See DECISIONS.md for architecture choices and WINNER_REFERENCES.md for a small verified reference review. LOCAL_HANDOFF.md assigns only runtime-dependent scanner work locally, starting with the read-only scripts/inspect_local.py report. The repository is now available at https://github.com/sevenhiremath/coverageproof; use the remote main branch as the shared source of truth.

Verification for this increment: 33 tests pass, including saved/displayed alternative explanations and rejection of incomplete model decisions. Local capability script ran without scanner execution. Dependency setup was reproduced in a new virtual environment after the runtime reset.

## Working app update: finding review and local model provider
- 46 tests pass. Real HTTP application startup and /health plus index routes return 200.
- Analysts can accept a candidate for the report, mark it false-positive or request more investigation. Identity labels and written reasons are saved with an evidence digest. New evidence makes earlier reviews outdated. Acceptance does not claim exploit validation.
- Imports preserve unmatched normalized observations. The analyst can add them to the declared plan with source pointers intact; this does not execute a scanner. Older imports made before this table existed remain available in their raw artifacts.
- PDF snapshots include review decisions, reviewer reasons, unmatched observations and audit events. False positives remain traceable but are excluded from active severity totals.
- Ollama provider added for the already-installed local model. Uses schema output, local loopback endpoint, citation/scope validation and no API key. No model download. Provider request/validation/failure behavior is mock-tested; actual local inference is NOT yet verified.
- Fixed development planner proposing an initial plan again when all existing checks had completed.
- Current form status from user: PS-1 submitted; contact swayamhiremath@outlook.com. No further selection-form task is needed.
- Local assistant reports 33 earlier checkpoint tests passed in an isolated Docker container. This is user-supplied verification, not reproduced online. Genuine scanner integration evidence is still pending.

## Finding correlation and risk context update
- 61 tests pass on the current feature branch.
- Added one explicit cross-tool mapping: ZAP 10021 GET/no parameter and the registered HTTP nosniff check. Full canonical URL identity prevents merging distinct hosts, ports, paths and queries. Unknown issue IDs remain separate.
- Cases preserve source observation details, confidence labels, timestamps, identifiers and conflicting results. Different supplied severities remain visible; the highest is used for conservative ordering.
- Added attributed exposure, asset impact and analyst-stated validation with required evidence references. The interface, PDF and model context share these inputs. No numerical risk score or fabricated CVSS is produced.
- Details, alternatives, benefits, drawbacks and limits are in CORRELATION_AND_RISK.md. Tests use clearly synthetic fixtures; genuine native scanner and live AI validation remain pending.
