# Project status — 9 November 2026

The submission application is on [deploy/render-demo](https://github.com/sevenhiremath/coverageproof/tree/deploy/render-demo).

The recorded demonstration completes an owned HTTP assessment with human approval, evidence inspection and PDF export. Planning in the recording uses labeled development rules.

Nmap, Nikto and ZAP have native result imports. Separate local validation reports record successful genuine Nikto and ZAP imports. These runs do not mean the web application launches the scanners. Groq selected a valid follow-up in a separate successful experiment. Later evaluation encountered rate limits.

The application supports a bounded HTTP header check. Broader scanner execution, a combined multi-tool demonstration and reliable AI behavior across many cases remain incomplete. Findings need analyst review.

The latest checked application commit is 2e88eec9dfb26006bd7c17e43edd28e479a591a1. Its GitHub workflow passed tests, browser and owned-nmap jobs. Documentation changes after this commit do not constitute another application test.

The repository includes a [historical owned HTTP sample report](../samples/current-owned-http/sample-vapt.pdf) and its [recording context](../samples/current-owned-http/README.md). It is separate from the November 9 video assessment.

## Historical development record

The notes below describe earlier checkpoints. Use the status above for the submission overview.

# Current delivery reference — November 4, 2026

See [DELIVERY_PLAN.md](DELIVERY_PLAN.md) for the latest priorities and checkpoint evidence. The November 2 status below is historical and must not be used as the current model or scanner result.

# Current project status — November 2, 2026

## What works and was checked

- 102 pytest tests pass online on Python 3.12. One upstream Starlette/httpx deprecation warning remains. Handwritten scanner format tests and injected failures are synthetic and labeled; a separate regression uses genuine Nmap output. Provider tests are mocked.
- Durable request → scope → declared checks → explained proposal → exact-action approval → bounded HTTP execution/import → evidence → findings/review → PDF workflow.
- Network/port/address/path exclusions, conservative URL validation, one-use approvals, denial audits, output/time/concurrency bounds. Native scanner execution remains disabled.
- Nmap XML, Nikto multi-host JSON and ZAP traditional JSON parsers implemented. Genuine Nmap 7.93 recording and app import verified in network-none GitHub containers (run 41477132439). Nikto/ZAP genuine output verification is still pending.
- Explicit cross-tool nosniff mapping, preserved disagreements, attributed risk inputs, evidence-bound finding review and before-execution applicability review.
- Collection-time windows distinguish current, stale, unknown and future evidence. Import time cannot refresh an old negative receipt.
- Real self-owned HTTP experiment rerun: two assessments have equal issue counts [1,1]; the second has an unattempted admin check. Approved follow-up updates that check to condition_not_observed while issue count stays 1. Development rules were used, not live AI. Sample size two; no accuracy or time-saving claim.
- Current report generated from that experiment; all four pages rendered and inspected. PDF/state consistency is tested. The final report layout must be checked after genuine evidence is added.
- GitHub container backend test job passed on commit 3292905. Its first run exposed a PDF-text test that depended on font wrapping; the assertion now normalizes whitespace while still requiring the full sentence. The genuine owned Nmap recording job also passed on commit 8d18830; native XML, manifest and containment record are in samples/recorded-nmap/. Runtime disables external networking, capabilities and writes outside bounded temporary storage.

## External work needed next

1. Approve the exact owned Nikto/ZAP plan in WEB_CHECK_PLAN.md. Official images, help and versions were inspected online in run 41478631044; no web scan has run. Genuine Nmap is already recorded online, so local scanner setup is unnecessary.
2. Local Ollama genuinely failed on 6831839: unknown check name after 167.42 seconds whole-command time. No fallback or follow-up ran. Notes are in LOCAL_MODEL_BROWSER_CHECK.md. The action enum/private diagnostics fix is regression-tested; follow MODEL_RETRY.md to verify it with the existing model. No live success claimed.
3. Local assistant reports the real saved-state three-page PDF and download passed visual inspection, with two Poppler font warnings. Browser automation was blocked by CLI_REGISTRATION_UNAVAILABLE; report-draft acceptance/staleness remain unverified locally. Real Chromium 156.0.8078.4 workflow, isolated backend tests and genuine Nmap import passed on final browser/PDF revision 419c2b0 in run 41489905357; desktop/mobile screenshots were inspected. Planning was development mode and report prose a labeled synthetic provider. Actual model prose/review remains pending.
4. Organizer evaluation scope is not supplied. Owned development fixtures do not establish organizer authorization.

## Remaining online implementation and delivery

Use returned native artifacts to fix genuine-format mismatches, add public self-owned regression samples, assess actual AI decisions and improve prompts/validation where observed failures justify changes. Grounded Ollama report drafting is implemented and unit-tested: schema/citations are validated, analyst acceptance is required, and changes invalidate earlier drafts. Actual model quality and final report layout still need local validation, then rerun the full demonstration. Manual interrupted-job recovery is implemented with an audit reason and no automatic retry; workers must first be stopped. Automatic recovery and broad issue mappings remain limitations. Native live scanner runners are optional if three genuine supported imports satisfy PS-1.

Prepare slides and a 1–3 minute own-voice demonstration from observed behavior, with accessible Drive links checked before the user authorizes final submission. Do not invent results or publish links on the user's behalf.

## Coordination

Canonical public source: https://github.com/sevenhiremath/coverageproof . Changes use feature branches and reviewed/tested pull requests; no force pushes. The user confirms PS-1/mentorship form submission. No further form task is needed. No final submission or organizer message has been sent.
