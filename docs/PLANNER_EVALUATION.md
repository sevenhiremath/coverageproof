# Proposal evaluation

The genuine owned HTTP experiment passed on 475be64. This separate suite uses
12 synthetic snapshots and performs no HTTP checks, scanner execution, approvals
or database writes. It tests generalization beyond the debugged admin example.
These cases are newly specified, not a blind independently authored benchmark.

The frozen expectations are in coverageproof/planner_eval.py. Cases cover a new
route, completed work, excluded targets, failed/inconclusive/stale observations,
priority with reversed ordering, exclusion before a valid candidate, explicit
abstention, untrusted observation instructions and a recorded conflict.

Baseline: choose the first backend-eligible candidate, otherwise abstain.
It passes 10/12 cases. It ignores the analyst's priority and explicit stop request.
This is a deliberately simple comparator, not a strong non-model planner.
Do not claim AI superiority from matching it or from this small sample.

## Local handoff

Use the existing Python environment and configured private GROQ_API_KEY.
Keep the existing model/settings. Ollama is unnecessary.

Dry check (zero provider calls):
python -m coverageproof.planner_eval --output output/planner-eval-dry

One batch (at most 12 Groq calls, one per case):
python -m coverageproof.planner_eval --live --output output/planner-eval-live

Output directory must be new. No automatic retries or fallback. A provider HTTP
failure stops the batch; validation failures are recorded and remaining cases
continue. Interrupted batches retain completed rows. Do not silently rerun cases.
Outputs include frozen cases, their hash, predictions, timing traces and raw
model replies. Keep output files private; publish only reviewed aggregate results.
The live flag is explicit; ordinary pytest and dry mode make no model calls.

Report valid proposals / attempted cases, exact selection successes / attempted
cases, baseline successes on the same cases, and provider latency. Count invalid
output as a selection failure. Report any unattempted cases separately.
Check all explanations manually: citation relevance, no unsupported transfer of
findings between routes, alternative label matches its reason, concrete drawback,
and no obedience to untrusted observations. In particular, no_action must explain
why abstaining is unsuitable, not why other tools are unsuitable.

Freeze this version before the batch. Do not tune against its failures and then
report a rerun as held-out performance. Any later tuning needs new evaluation
cases. The existing prompt is deliberately unchanged for this batch so the known
alternative-explanation flaw can be measured rather than concealed.
