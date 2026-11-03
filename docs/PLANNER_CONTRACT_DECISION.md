# Planner contract decision

Decision: use candidate-ID selection for follow-up planning, with typed basis references. Preserve AI prioritization, explanation and abstention. Initial plan creation remains a separate existing flow. This document specifies proposed implementation; it does not claim the contract is already changed.

## Evidence and limits
The bounded owned HTTP run passed on 475be64. The evaluation on 40db03b attempted five cases: three correct/valid proposals, one undeclared action rejected, and one HTTP 429; baseline 5/5 on that prefix. Seven cases were unattempted. Citation IDs existed but some claims were unsupported. These results do not establish general model inferiority, superiority or prompt-injection robustness. PR11 adds guidance but does not guarantee grounding.

## Contract
1. Backend supplies eligible candidates with opaque check IDs, exact stored actions, state and execution availability. Model returns selected candidate IDs, rationale and basis references; it does not reproduce targets, ports or scope revisions. Reject unknown or duplicate IDs. Resolve IDs against the same snapshot, then revalidate current scope and eligibility before accepting. Exact execution approval remains a later operation.
2. Basis references distinguish check IDs (an unanswered question), observation IDs (a recorded result) and finding/conflict IDs (a recorded disagreement). Require at least one applicable basis for a selection. An unattempted check may cite itself as the coverage gap without citing an unrelated root observation. A basis reference proves existence, not truth of free-form reasoning.
3. Keep outcome and freshness beside every observation. Failed/inconclusive receipts cannot support presence or absence claims. Validate structured basis types and relationships deterministically; present prose as an analyst-reviewed model explanation. Do not claim semantic validation from ID validation.
4. Represent alternatives explicitly as abstention or another candidate. Require a reason tied to that alternative. Derive tool names from candidates rather than asking the model to relabel tools. Keep concrete limitations visible from the registry; label any additional model-generated drawback separately.
5. If there are no eligible candidates, return a clearly attributed backend eligibility result without a provider call. Do not call that AI abstention. AI abstention is evaluated when eligible actions exist but the analyst request calls for stopping or supplies insufficient information.
6. Provider failure produces an unavailable planning result with manual candidate selection available. No fabricated model decision or automatic development fallback.

## Why this choice
It directly removes action-copying errors and the incentive to cite unrelated observations. It retains an actual model decision among permitted options and the ability to abstain. The cost is a new response schema, adapter and migration tests. Existing stored decisions should remain readable; label contract versions and retain raw model outputs.

More prompt text alone is cheaper but leaves these structural errors possible. Making AI only narrate a deterministic choice reduces the adaptive role before we have tested meaningful competing choices. Switching models adds cost/variance without resolving the contract defects. We therefore choose a bounded contract change, not a provider switch or broad rewrite.

## Evaluation corrections before new calls
Keep the original result immutable. Build new cases from Store snapshots where practical: the previous synthetic stale receipt used a coverage state as a receipt outcome, and the conflict case marked a conflict with only one observation. These fixtures exercise branches but do not faithfully represent evidence histories. Include failed attempts with no receipt, genuine opposing receipts, stale timestamps, multiple tool candidates, priority ordering and abstention with eligible actions. Freeze expected acceptable selections before calling the model. Score policy validity, task selection, citation relationship and human-reviewed semantic support separately. Track provider availability separately while still counting failed calls in end-to-end success.

Add explicit batch completion/stop status and non-success process status for interrupted/provider-failed evaluation. Write frozen cases as UTF-8 bytes so the declared SHA256 matches disk bytes on Windows and Linux. Persist quota/retry timing headers if available without error bodies or secrets. Honor observed provider guidance for later batches; do not infer that 429 means a particular quota or launch automatic retries.

## Implementation order
Sol: implement the follow-up selection adapter and versioned decision format; test invalid/duplicate IDs, changed scope, empty eligibility and typed basis relations. Then repair evaluation fixture realism and output status/hash handling. Prepare a new frozen suite before one bounded local evaluation. Preserve the existing initial-plan flow and execution approval boundary.

Do not postpone genuine Nikto/ZAP integration proof, report/UI completion and the submission demo indefinitely for model tuning. The planner contract change should remain a small isolated PR. A larger agent framework, new database or provider migration needs another architecture review.
