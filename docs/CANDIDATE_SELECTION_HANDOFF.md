# Candidate selection implementation

Follow-up model output uses selections with candidate IDs and typed check,
observation or finding bases. The adapter resolves stored actions and preserves
the legacy proposal display shape, with contract_version=candidate-v2. Existing
stored decisions and initial model plans remain legacy-v1. Groq, Ollama and
OpenAI follow-up providers use the new schema. Development rules remain labelled.

Unknown/duplicate candidates and unrelated basis references are rejected.
Current scope/eligibility is checked again before saving. Exact execution approval
remains separate. Empty eligibility records backend provenance without an AI call.
Prose still requires analyst review; matching IDs do not prove semantic grounding.

The evaluation fixtures now distinguish stale coverage from receipt outcome,
use opposing observations for conflict, and avoid a finding receipt for failure.
The frozen cases are written as UTF-8 bytes for portable hashing. Results carry
completion status; provider-stopped CLI runs exit 2.

The original batch on 40db03b is preserved and must not be relabelled. This suite
has changed and needs a fresh output directory and new suite hash. It remains a
developer-authored regression suite, not independent held-out evidence. The
evaluation invokes the provider directly to assess model abstention even for
empty eligibility; the application skips those calls and labels backend results.

No live calls were made during implementation. Before another batch, inspect
account quota/provider guidance privately. Do not retry the previous 429 batch
automatically. Run the dry evaluation and tests first. Keep model outputs private.
A genuine owned experiment with the new schema and a freshly frozen live suite
remain pending; no live quality or reliability improvement is claimed.

Remaining follow-up: Store-generated evaluation fixtures, fresh multi-tool
candidate cases, quota timing metadata and browser presentation of typed bases.
Continue genuine scanner integration proof and report/demo work in parallel with
the planner milestones; no new agent framework or provider switch is needed.
