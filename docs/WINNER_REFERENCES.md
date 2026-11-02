# Useful ideas from winning projects

Read on November 2, 2026. No reference repository was executed, copied or added as a dependency. These are adjacent projects, not direct evidence that CoverageProof will win.

## Team Atlanta / Atlantis
DARPA names Team Atlanta first in the 2025 AI Cyber Challenge. The public Atlantis repository separates its main implementation, infrastructure and supporting utilities. Useful idea for us: keep the app, runner boundary and lab setup understandable as separate responsibilities. We retain a small Python app rather than copying a competition-scale system. The root repository lists MIT; any actual reuse still requires checking the exact files and notices.
Sources: https://www.darpa.mil/news/2025/aixcc-results ; https://github.com/Team-Atlanta/aixcc-afc-atlantis

## Trail of Bits / Buttercup
DARPA names Trail of Bits second. Buttercup's README describes AI-assisted discovery and repair, a coordinating component and explicit model-budget controls, plus tests at several integration levels. Useful ideas: separate proposing from evidence-producing verification; keep provider calls observable; add a bounded model-call budget before repeated planning is enabled. Budget control is a planned improvement, not implemented here. We do not adopt its multi-agent patching infrastructure: different task, larger compute/deployment needs and unnecessary scope. Root repository lists AGPL-3.0; no code is copied.
Sources: https://www.darpa.mil/news/2025/aixcc-results ; https://github.com/trailofbits/buttercup ; https://raw.githubusercontent.com/trailofbits/buttercup/main/README.md

## Banshee / Hack Indy 2026
Devpost lists Banshee as 4th Place - Honorable Mention, not the grand-prize winner. Its creator describes a specific voice-AI assessment workflow, recorded interactions and analysis of the resulting transcripts. Useful product lesson: show one concrete task and inspect its evidence in the demo. CoverageProof's equivalent is an assessment gap, its supporting observations and the approved next check. We do not add voice attacks or telephony dependencies. This is a creator-reported implementation description, not independently reproduced performance. No code or assets reused; licensing review would be required before reuse.
Source: https://devpost.com/software/banshee-2s4for

## What we take forward
Evidence-producing checks, clear separation of responsibilities, understandable demonstrations and bounded AI use. Award placement alone does not explain why a project won; these are our engineering judgments from the inspected materials.

## Closer benchmark: SANS Find Evil! winners

Organizer announcement checked November 2, 2026: Mulder placed first and TRUDI second. SANS describes source-challenging in Mulder and server-side constraints/self-correction in TRUDI. These are forensic agents, not PS-1 VAPT products. We have not reproduced their results.

Our interpretation: test evidence claims and enforce permissions in code. CoverageProof already preserves disagreements, rejects nonexistent citations and binds approvals to exact actions. It still lacks their reported independent evaluation. Repository metadata lists Mulder Apache-2.0 and TRUDI MIT; no code copied or run.

Sources: https://www.sans.org/press/announcements/sans-names-the-five-winners-of-find-evil-2026 ; https://github.com/calebevans/mulder ; https://github.com/nebulae/trudi

## What “as good” should mean for our submission

Award placement is not a comparable performance score. We cannot claim to outperform these systems: tasks, data and resources differ. Our practical acceptance gates are:

| Gate | Benefit | Trade-off / current gap | Required evidence |
|---|---|---|---|
| Explain an important missing check despite equal issue counts | Demonstrates our actual contribution | Tiny HTTP experiment alone is insufficient | Genuine native artifacts plus actual model decision |
| Challenge conflicting observations | Avoids trusting the latest tool blindly | A fresh check may not resolve historical differences | Both source artifacts, timestamps and targeted follow-up |
| Enforce permission outside the model | A convincing explanation cannot authorize a scan | Deliberately limited action registry | Denial, approval binding and replay tests |
| Trace report claims to evidence | Judges can inspect why a result exists | Analyst judgments still require review | Source pointer, hash, state and immutable report snapshot |
| Reproduce the demo smoothly | Makes the work understandable in under three minutes | Smaller scope than large winning platforms | Clean setup, real browser run, recorded timing and limitations |

Prefer these gates over copying a winner's full architecture. Broader autonomous systems add testing, runtime and explanation costs that do not help us close the mandatory baseline first.
