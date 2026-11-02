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
