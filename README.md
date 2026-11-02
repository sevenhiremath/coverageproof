# CoverageProof

What did we assess, what remains unknown, and what should we investigate next?

CoverageProof is a PS-1 assessment workspace for the DataOps Innovation Hackathon 2026. Coverage means evidence for explicitly declared checks, never completeness against all vulnerabilities.

## Run

Python 3.11+:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
python -m uvicorn coverageproof.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Windows: activate with `.venv\Scripts\Activate.ps1`. Configuration is documented in `.env.example`; export environment variables explicitly (no automatic dotenv loading). Database defaults to `data/coverageproof.sqlite` and persists across restarts. Keep it private; it contains raw assessment evidence.

1. Create a request with an explicitly authorized literal-IP network scope and allowed ports.
2. Generate a plan (explicitly labeled deterministic development mode unless model secrets configured).
3. Inspect a declared check, approve the exact HTTP action, then execute it against your own fixture.
4. Import native scanner outputs for already-declared exact targets; imports remain labeled imports.
5. Inspect observations and gaps. Download the assessment PDF.

## Checkpoint status

Working: durable declared-check workflow, exact-action one-use approvals, network/port/exclusion policy, Nmap/Nikto/ZAP native parsers, evidence hashes and pointers, coverage states, bounded HTTP runner, provider contract, development planner, findings candidates, downloadable report snapshots, Jinja interface and automated tests.

Not submission ready: genuine three-scanner lab output verification, organizer lab access, live AI evaluation, cross-tool issue mappings, stronger risk contextualization and native isolated scanner runner. No deterministic response is represented as live AI reasoning. Read [status](docs/STATUS.md) before making capability claims.

## Evidence experiment

```bash
python scripts/experiment.py
```

Uses a real self-owned HTTP fixture. Generates evidence and a PDF in `output/`. This validates the workflow contribution with a real bounded HTTP check; it does **not** replace the required genuine three-tool demonstration. Unit-test scanner strings are synthetic schema fixtures, never demo scanner results.

## Documentation

- [Requirements and exact document sections](docs/REQUIREMENTS.md)
- [All-seven integration matrix](docs/INTEGRATIONS.md)
- [Architecture and boundaries](docs/ARCHITECTURE.md)
- [Why we chose these approaches](docs/DECISIONS.md)
- [Useful ideas from winning projects](docs/WINNER_REFERENCES.md)
- [Local scanner handoff](docs/LOCAL_HANDOFF.md)
- [Syncing online and local work](docs/SYNC.md)
- [Status / handoff](docs/STATUS.md)
- [Submission readiness](docs/SUBMISSION.md)
- [Dependency licenses and references](THIRD_PARTY.md)

AI-assisted implementation. No upstream application code has been copied into this checkpoint. Third-party dependencies and format documentation remain their authors' work.

## Local AI without a paid API

The app now supports the model already installed in Ollama. Set these environment variables before starting the app on that same machine:

```text
COVERAGEPROOF_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:9b
```

The provider calls `http://127.0.0.1:11434/api/chat`, requests JSON matching the plan schema, and applies the same evidence/scope checks. It does not download models or use subscription credentials. Keep default development mode if Ollama is unavailable. Failures are recorded and do not silently become development answers. Actual local-model quality/speed remains unverified; automated provider tests use synthetic mocked responses.

## Finding review

Inspect a candidate's source evidence, enter a review reason and choose accepted for report, false positive or needs review. New evidence invalidates the earlier review. False positives remain available for traceability. Imported observations without matching declared checks are displayed separately and can be added to the plan after inspection.
