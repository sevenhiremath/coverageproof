# Why we made these choices

We explain the main engineering and assessment choices in plain language. Each note states the task, chosen approach, useful alternatives, drawback and verification. These are decision summaries, not a claim that every private model thought is stored or correct.

| Choice | Why it fits this project | Alternative we considered | Why we did not choose it now | Drawback of our choice |
|---|---|---|---|---|
| FastAPI | Python request validation and a small web app in one place | Flask; Django | Flask needs more validation wiring; Django adds features we do not yet need | We still have to build access control and job handling properly |
| SQLite | Easy setup, durable evidence and transactional approvals for one analyst | PostgreSQL | An extra server is not needed for this initial workload | Limited concurrent writes; not a multi-user production design |
| Jinja pages | Lets us finish the analyst workflow without a separate frontend build | React | A separate client would add state and build work before the baseline is complete | Rich interactions need more server round trips |
| Nmap + Nikto + ZAP imports first | PS-1 accepts native imports; network and web formats can be verified separately | Immediately run all scanners inside the web app | Online runtime has no scanners/Docker; unrestricted subprocess execution would be unsafe | Imports do not demonstrate live orchestration; genuine format tests are still required |
| Separate restricted runner | Approved actions map to fixed code, not model-written shell | LLM-generated commands | Commands can bypass scope or introduce unsafe flags | Every new action requires a supported template and policy tests |
| AI for planning and explanations | Requests and follow-up questions need contextual interpretation | Fixed scanner sequence | Fixed order cannot reasonably explain different next steps for different evidence | AI may hallucinate; schema, citations and policy validation are necessary |
| Deterministic scope and approval policy | Permission must be predictable and testable | Ask the model whether an action is allowed | A persuasive explanation is not authorization | Scope rules are deliberately narrow; hostname/path controls need further work |
| Explicit checks and evidence | Makes unattempted, failed and contradictory work visible | Count and deduplicate findings only | Equal finding counts can hide different assessment gaps | Analysts must declare meaningful checks; the plan cannot represent all possible vulnerabilities |
| Keep uncertainty in findings-only exports | Missing alerts do not prove a rule ran or a route was reached | Treat zero alerts as a pass | That would overstate what the scanner output establishes | More checks stay inconclusive until stronger evidence arrives |
| Small model provider interface | Supports real AI without tying permission decisions to a framework | Agent swarm; model training | Adds complexity/cost without meeting this short project's immediate needs | Provider/model availability and grounding still need live verification |
| ReportLab PDF snapshots | Reports can freeze stored evidence/state and be tested | LLM writes the final report freely | Free-form text could contradict saved results | Layout work is manual and report narrative drafting remains pending |

## Writing and commits
Use short direct descriptions: 'Add reasons for suggested checks', 'Fix imports with missing ports', 'Keep both results when tools disagree'. Explain technical terms when they help. Avoid inflated claims such as 'enterprise-grade', 'fully autonomous' and 'production-ready'. Keep AI-assistance disclosure and required third-party notices. Simple wording does not mean pretending AI-written work was entirely human-written.

## Reason for each proposed assessment check
Record: selected action; why useful now; source observation IDs; a relevant alternative and why it was not selected for this task; a concrete limitation; approval/policy outcome. Model proposals without alternatives or a limitation are rejected. The backend verifies structure, scope and evidence IDs, not whether the prose is scientifically correct. Human review and model evaluation still matter.

## Why we added a local model provider
The user already has an Ollama model and no paid API access. The app can therefore call a local model through its documented JSON-schema interface. The alternative is a paid model API; it adds a cost/account dependency that is unnecessary for initial integration. The drawback is variable local speed and model quality, so provider behavior is tested separately from the still-pending actual model evaluation. Nothing silently substitutes development rules for a failed model call.

## Why reviews are tied to evidence
A review applies to the observations the analyst actually saw. Automatically carrying that review over to later imports could hide new contradictions. We therefore record the evidence digest and mark changed findings for review again. This is conservative: even a duplicate reimport prompts another review because it adds an evidence record.

## Grouping and prioritization choices
See CORRELATION_AND_RISK.md for the alternatives table, exact matching boundaries, why we avoid title/LLM-only merging, and why we use attributed risk inputs instead of an invented score. These are implemented choices with tested limits, not claims of full production accuracy.
