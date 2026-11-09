# Give the planner explicit policy facts

The local retry on bcbc3eb produced valid JSON but repeated the completed root check after incorrectly treating /admin as excluded by allowed_paths=["/"]. The backend defines / as the root subtree. Increasing the timeout cannot correct that reasoning error.

The planner context now includes eligible declared follow-ups, exact actions, backend policy verdicts and live-versus-import availability. For an existing plan, model proposals must select one of these actions or return an empty list. Completed checks are excluded unless a recorded conflict justifies investigation. Exclusions still win. No choice grants execution approval.

This is the first bounded repair, preserving the existing action JSON contract. A later candidate-ID contract can further reduce output complexity. Initial planning without declared checks remains registry/scope validated and is not restricted by this follow-up list. Model explanations can still be wrong; this change does not establish useful AI reasoning.

| Choice | Benefit | Alternative | Drawback |
|---|---|---|---|
| Supply backend policy verdicts | Model need not infer path semantics | Prompt-only correction can repeat the same mistake | Candidate construction must stay consistent with policy |
| Reject completed-action repetition | The observed wrong choice fails before plan mutation | Accept every scoped action: valid permission does not imply useful work | Intentional retesting needs a recorded conflict or a separate explicit analyst action |
| Keep several eligible actions and allow no action | Preserves actual model choice and abstention | Force the only expected demo answer | Correct selection and relevant explanation still require evaluation |
| Preserve existing output contract initially | Small regression surface | Candidate-ID rewrite across providers and diagnostics | More output tokens than an ID-only response |

Regression cases cover root subtree semantics, exclusions, multiple options, import-only labeling, repeated completed actions, conflicts and abstention. These are synthetic contract tests, not live-model results.

## Exact next local task

Fetch branch fix/planner-scope-context into a fresh worktree. Preserve other branches. Use the existing Python environment and installed Ollama model. Follow docs/MODEL_RETRY.md using this branch instead of main. Do not repeat hardware inspection, scanner setup or model downloads. Run scripts/experiment.py once with COVERAGEPROOF_PROVIDER=ollama and preserve the exact response, diagnostics, timings and state, including failures. Do not change prompts or substitute development mode. Return notes on a new local branch and keep raw evidence private.

A successful run only verifies this small experiment. Multiple-choice and held-out evaluation remain necessary before any quality claim. The experiment summary now records model provenance before testing decision usefulness, so an accepted but unhelpful model choice no longer leaves planner_mode null.
