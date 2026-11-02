# Architecture

Browser → FastAPI/Jinja workspace → SQLite store → immutable evidence + observations → coverage reducer → findings/PDF snapshot.

Planner receives registered checks, request, scope and prior receipts. Provider structured output is validated by Pydantic, target policy and observation-ID validation. Proposals only append checks/decision events. They cannot execute actions. No raw shell or user-selected tool options exist.

Runner claim transaction binds a one-use approval to the complete scope document and exact action, and enforces one running job. Runner revalidates scope, maps the check to a registered implementation, and records terminal state. Native CLI execution is currently disabled; the HTTP boundary uses literal IPs, no redirects, no environment proxies, a timeout and bounded output. This is logical separation in one process, not an OS sandbox. An isolated scanner process with egress restriction remains required for native live scanners.

SQLite tables: assessments (versioned scope snapshot), checks, approvals, attempts, artifacts (raw bytes/hash), observations (source pointers), decision events, report snapshots. Asset identity is a canonical literal IP/URL; no speculative hostname/IP merging. Finding candidates are derived and preserve every matching evidence link. Reports freeze the complete state and hash the PDF; no LLM text can alter authoritative finding/approval/execution state.

The loopback UI is a single analyst tool. Host/Origin checks prevent common cross-site/rebinding mutations; no multi-user authentication or role assignment is claimed. Do not expose directly to the internet. Analyst names are audit labels, not verified identities.

Crash recovery for jobs left running and artifact encryption remain pending. Path boundaries and collection-time windows are enforced; unknown timestamps remain uncertain. Applicability reviews are tied to scope/action and invalidated by execution or evidence. Finding review disposition now records the analyst decision and evidence digest. No automatic final-report approval is claimed.
