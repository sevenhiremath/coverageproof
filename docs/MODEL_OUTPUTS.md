# Why invalid model actions are constrained and recorded

The genuine local run on 6831839 returned an unknown registered check after 167.42 seconds total. The backend rejected it, but the JSON Schema described action.check as any string: its Python validator was not represented in the schema. That was an implementation gap; without the complete rejected JSON we cannot explain the model's full decision.

Now action.check is limited to the four registered names in both schema and backend validation. Model provenance is constrained, the schema is also included in the prompt, and unfinished declared checks appear explicitly in context. No-action means checks=[], never an alias or automatic conversion to a real action. This reduces invalid output; it does not guarantee useful reasoning or correct citations.

| Choice | Benefit | Alternative and why we skipped it | Drawback |
|---|---|---|---|
| Explicit action enum | The provider sees the actual legal names | Silently rename invented actions: could hide a wrong decision | The registry and schema must be updated together |
| Private rejected message JSON with timing/hash | A real failure can be reproduced and diagnosed | Print the whole reply in errors/events: may disclose sensitive evidence | Private database/export needs careful handling |
| No automatic development fallback or blind retry | Preserves the actual model outcome | Pretend a rule-based check was the AI decision: misleading | Actual local verification is still needed |
| Keep timeout unchanged | The observed error was validation, not timeout | Increase timeout without evidence: does not fix action names | The next run may still be slow or fail |

Ollama model calls record purpose, requested/reported model, provider-call elapsed milliseconds, returned timing/token metadata when present, outcome, safe validation locations and hashes. Valid/invalid message.content is retained byte-for-byte as UTF-8, up to the existing 256-KiB response bound. Thinking text, request headers and full malformed envelopes are not retained. Incomplete/oversized responses remain unusable. Raw output has no UI/download route and is excluded from assessment snapshots and PDFs; audit metadata links to the private call ID. Accepted proposal prose still appears in the normal decision audit.

The experiment exports current state even on failure. For an explicit private export from an existing database:

```bash
python scripts/export_model_calls.py --db output/experiment.sqlite --assessment ASSESSMENT_ID --out output/private-model-export
```

Use a new output directory; existing files are not overwritten. Do not commit exports or the database. Schemas, privacy boundaries and failure-state export are regression-tested with synthetic responses, not claimed as live-model success.

Source: Ollama's official structured-output documentation recommends passing a JSON schema through format and grounding it in the prompt: https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx . No upstream code copied.
