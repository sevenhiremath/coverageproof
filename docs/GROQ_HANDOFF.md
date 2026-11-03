# First live Groq check

Use branch feature/groq-provider in a fresh worktree, preserving older work. Use the existing Python environment with this worktree on PYTHONPATH. The key must already be in the process environment; never print it, paste it into chat or commit it.

PowerShell, from the new worktree (replace the Python path with the existing environment):

```powershell
$env:COVERAGEPROOF_PROVIDER='groq'
$env:GROQ_MODEL='openai/gpt-oss-120b'
$env:PYTHONPATH='.'
python scripts/experiment.py
```

Run once against the script's own benign HTTP fixture. This sends the assessment request, scope, candidate actions and observation excerpts to Groq. Use only this non-sensitive fixture. No Ollama, model downloads or scanners are required. Do not substitute development mode, change assertions or repeat failed calls automatically.

Return source commit, selected action, overall elapsed time and saved provider elapsed_ms. Preserve output/experiment-summary.json, database, HTTP receipts, PDF and model-diagnostics privately. Commit only non-sensitive result notes on a new local branch. If HTTP 401, 429 or a model/schema error occurs, report its status without key or provider body. The online tests are mocked; no live success has been established yet.

Expected result: actual model mode; /admin changes from unattempted to condition_not_observed after its exact approved follow-up; issue count stays one. A failed or empty proposal is retained without a substituted action.

## Choice and limitations

Groq uses its documented OpenAI-compatible chat endpoint and best-effort JSON schema mode. This fits the existing Pydantic schema without changing optional fields. Strict schema mode is an alternative requiring schema conversion; regardless of mode, valid JSON cannot establish good reasoning. Backend scope, eligible-action and citation checks remain required.

The default model is openai/gpt-oss-120b, configurable with GROQ_MODEL. Actual account availability, quota, quality and latency need this live test. One bounded request, 2048 completion tokens, 60-second HTTP timeout, 256-KiB response bound, no redirects/environment proxy and no automatic retry limit failure amplification. The timeout is an HTTP timeout, not a guaranteed process wall-clock deadline. Credentials and error bodies are excluded from saved diagnostics. Only message content is saved privately, not reasoning fields.

Planning and analyst-reviewed report drafting support Groq. Reports retain actual provider labels. The benefit is hosted inference without local model tuning. The drawbacks are network/account dependency and sending context to an external service. Ollama remains optional; neither provider silently replaces a failed call.

Official references inspected November 3, 2026:
- https://console.groq.com/docs/openai
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/model/openai/gpt-oss-120b
