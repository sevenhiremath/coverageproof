# Store-built evaluation v2

Freeze six synthetic cases with `python -m coverageproof.store_eval --output NEW_DIRECTORY`. The v2 fixture declares a separate root Nikto check before importing root evidence. This makes the untrusted instruction visible in the actual model context while preserving three unanswered admin candidates. Every case asserts model-input exposure. The previous v1 freeze stored that text as unmatched evidence, omitted by model_context; it cannot establish resistance to scanner instructions. Preserve existing evidence as v1.

The request-aware baseline reads only the analyst request's first clause and selects the matching eligible HTTP or ZAP candidate, or abstains. It is explicitly tailored to this suite's vocabulary and scores 6/6 offline. First eligible and HTTP-first score 1/6 and 2/6. These are instruction-following checks, not independent security expertise or evidence that a model is superior to rules.

Evaluate the same frozen bytes with:

```
python -m coverageproof.frozen_eval --cases NEW_DIRECTORY/cases.json --sha256 HASH_FROM_SUMMARY --output NEW_RESULT_DIRECTORY
```

Add `--live` only for an authorized bounded Groq run: at most six calls, no retries, stop on provider failure including 429. No scanner, approval or target execution occurs. The evaluator verifies the hash and input exposure before any calls, copies exact case bytes, saves raw provider envelopes and traces, validates candidate-v2 proposals, and scores exact candidate IDs. Interrupted cases remain unattempted. Explanations require manual review of citation meaning, abstention, alternatives and limitations. Schema validity alone is insufficient.

UUIDs and timestamps differ across freezes; reuse cases.json and its SHA256 for comparisons. Use a fresh output directory. Private provider outputs and synthetic databases should remain in the private diagnostics bundle. No live model quality claim is established by offline verification.
