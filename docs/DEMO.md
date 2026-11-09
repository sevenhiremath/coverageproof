# Submitted demo workflow

The prepared recording lasts about 2 minutes 46 seconds and uses the participant's own narration.

1. Explain how a failed or unattempted check can leave an assessment incomplete.
2. Introduce CoverageProof and inspect the home-page finding and pending admin check.
3. Request the next check using labeled development planning.
4. Approve the exact admin HTTP check and execute it.
5. Inspect the result and the unchanged finding count.
6. Inspect evidence and download the assessment PDF.

The recording demonstrates the HTTP workflow. Groq and native scanner imports were evaluated separately. The presentation follows the organizer's nine required sections in order.

The form asks for a public-view Google Drive presentation link, a public-view Google Drive video link and the GitHub repository URL. Review permissions before submitting.

## Earlier planning notes

The following outline is historical and includes features that are absent from the finished recording.

# Demo and presentation draft

Current delivery order and official rubric: [DELIVERY_PLAN.md](DELIVERY_PLAN.md). Prioritize the complete assessment-agent journey, genuine cross-tool correlation and defensible risk before stretch retesting.

Target recording: 2 minutes 45 seconds, the participant's own voice. No AI narration. Record only verified behavior from the final candidate; this is a script outline, not a claim that all steps have passed. Leave at least a day for failed recording/setup fixes before the November 7 deadline.

| Time | Show | Explain in plain language | Evidence / readiness |
|---|---|---|---|
| 0:00–0:20 | Two assessments with equal issue counts | “The same issue count can hide a missing assessment check.” | Genuine owned HTTP experiment exists; full model/scanner demo still pending |
| 0:20–0:40 | Scope, declared condition, unattempted route | “We know what was checked and can point to what is still unknown. We have not invented a vulnerability here.” | Exact scope and state with source artifact |
| 0:40–1:10 | Actual model proposal, citations and rejected alternative | “This check answers the missing question. Here is why this tool fits, why we skipped another and what it cannot tell us.” | One genuine Groq candidate-v2 selection passed; final multi-candidate demo remains pending. Never show development rules as AI |
| 1:10–1:35 | Exact approval and bounded follow-up | “The model suggests; the backend checks permission. Only this action is approved.” | One-use approval, literal target, recorded outcome |
| 1:35–1:55 | Updated state and source evidence | “The condition was not observed in this response. That does not mean the whole app is secure.” | Before/after state and raw evidence, same finding count |
| 1:55–2:20 | Genuine tool imports and brief controls | “Imported outputs stay labeled imports. Conflicting results remain visible. Out-of-scope actions are blocked.” | Nmap genuine sample verified; Nikto/ZAP pending. Synthetic timeout must be labeled test injection |
| 2:20–2:45 | Reviewed explanations and downloadable PDF | “The report preserves what we know, failures and remaining limits. Every supported claim can be traced back.” | Real model draft/analyst review and final PDF/browser inspection pending |

## Five-slide content outline

1. Problem: finding totals hide missing work. Question: what did we assess and what remains unknown?
2. Contribution: declared checks, preserved evidence, explained next step, exact permission, updated assessment. AI helps interpret and explain; deterministic code controls actions.
3. Architecture: FastAPI/Jinja, SQLite, validated model provider, restricted action registry, imports and immutable report snapshots. Benefit: small and inspectable. Drawback: single-analyst loopback app with a small supported check set.
4. Observed experiment: two scripted owned HTTP assessments, issue counts [1,1], different completion, approved follow-up closes one declared gap. Sample size two. Native Nmap genuine import verified. Add real Nikto/ZAP and model results only after they exist. No invented accuracy or time-saving percentage.
5. Boundaries and next steps: no arbitrary shell/autonomous exploitation; three named integrations truthfully labeled; unknowns and failures retained; genuine lab/model limitations. Explain how this differs from a findings-only aggregator.

## Before recording

Use a fresh assessment with genuine non-sensitive evidence. Save the actual commit, tool/model versions, commands and artifacts. Verify the complete browser workflow, PDF pages, scope denial, conflict retention and bounded negative wording. Practice explaining the main files and why we chose these methods. Check that the public repository has no secrets or private lab information. Do not substitute an edited scanner output if the demo fails; show the error and fix its cause.

Only the user can authorize final submission or public presentation/video links. Drive presentation, Drive video and GitHub links must be accessible to judges. No final entry has been submitted.
