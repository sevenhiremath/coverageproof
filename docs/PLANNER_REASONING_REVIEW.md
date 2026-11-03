# Review after the partial live batch

Source batch: 40db03b. Reviewed local result:
https://github.com/sevenhiremath/coverageproof/blob/b077188/docs/LOCAL_PLANNER_EVALUATION_RESULT.md

Five cases were attempted before HTTP 429 stopped the batch. Three proposals
were valid and selected correctly; the baseline selected correctly on all five.
Four HTTP 200 responses included one backend-rejected undeclared action. Seven
cases were unattempted. This is no evidence of model superiority or a complete
12-case reliability score. Provider availability and reasoning errors both count
against operational usefulness, but have different causes.

Existing citation IDs did not establish semantic grounding. The failed-case
explanation claimed a condition result that its failed receipt did not support.
The no_action alternatives also failed to explain abstention.

## Targeted clarification

The shared planner prompt now explicitly forbids inventing actions when the
eligible list is empty. Each visible observation receives a backend-derived
description of what its outcome and freshness can support. Failed, inconclusive
and conflict receipts do not establish presence or absence of a finding. Stale
evidence is historical, while unknown/future timestamps do not establish a current
condition. The alternative reason schema describes no_action as abstention;
the prompt requires its explanation to address the cost of abstaining.

Why: these are known contract ambiguities with a small, reversible fix.
Alternative: automatically replace explanations or use keyword rejection. That
would conceal the original model behavior or reject valid prose without proving
grounding. We retain raw outputs and strict action/citation validation instead.
Limitation: explicit context is guidance, not a semantic proof. A model can still
misstate evidence. No live improvement is claimed.

The original suite and expectations remain unchanged. A rerun after this change
is a regression evaluation, not held-out performance. Do not automatically
continue or retry the rate-limited batch. Fresh live calls and fresh evaluation
cases remain pending. The untrusted-instruction case is still unverified.

## Architecture decision checkpoint

If fresh evaluation still yields weak reasoning, review whether AI should be
limited to explaining backend-selected candidates or whether a different planning
design is justified. That changes the product's AI role and warrants a deliberate
architecture review with the user. No provider switch, automatic fallback or
planner redesign is part of this clarification.
