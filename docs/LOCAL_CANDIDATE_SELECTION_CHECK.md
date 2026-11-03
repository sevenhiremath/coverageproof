# Local candidate-selection gate — November 4, 2026

Requested/source commit: `8ec08481dac44b55e31fd904394d2c437f380015`,
`feature/candidate-selection`. Fresh worktree and notes branch
`local/candidate-selection-check`; previous evidence/worktrees preserved.
Read CANDIDATE_SELECTION_HANDOFF.md. Used existing Python 3.14.4 environment,
with this worktree on PYTHONPATH. No downloads or dependency changes.

## Stopped at failed test gate

Command:

```powershell
$env:PYTHONPATH='.'
..\coverageproof-current\.venv\Scripts\python -m pytest -q
```

Result: **130 passed, 1 failed, 1 warning in 16.63s**, pytest exit **1**.
Whole command with log capture: **20.1684427 seconds**.
Started November 4, 2026 at 04:31:51.6411390 IST.
Failure:

```text
tests/test_recorded_nmap.py::test_owned_nmap_recording_is_preserved_and_interpretable
assert hashlib.sha256(raw).hexdigest() == manifest['sha256']
```

Read-only diagnosis:

- Manifest expected SHA256:
  `6c96a1bc3ce04d0474aecc3747ada86a767bb1dc5c6a702443a2ea0a35773877`.
- Committed Git blob SHA256 matches that expected value exactly.
- Windows working-copy SHA256:
  `c0009701aeb8e03b86e2e51b8d05e5c6bad687f7fb04a391a88d2869eb932d89`.
- Working copy has 19 CRLF pairs, Git blob has zero. Normalizing those pairs
  to LF in memory reproduces the committed blob exactly.
- No fixture bytes, Git settings, manifest or assertions were changed.

The one warning was upstream Starlette/httpx TestClient deprecation.

Per the user's stop-on-failure instruction, the dry evaluation and owned HTTP
experiment were **not started**. Groq calls: **0**. Selected candidate, typed
basis, explanation quality and approval/execution results: **not available**.
No automatic retry, fallback, Ollama start, scanner execution or scope action.
No key was loaded or printed. Raw test log, timing and fixture diagnosis remain
in private output files, with a hash-verified evidence archive.

## Smallest next step for review

Preserve recorded evidence byte-for-byte across platforms, for example by adding
an appropriate .gitattributes rule upstream. This fixes checkout conversion
rather than weakening integrity checks. An alternative is an LF-preserving fresh
checkout for validation; it is less durable because later clones can repeat the
problem. A repository rule requires reviewing which evidence formats must retain
their exact bytes. Verify the committed/checkout SHA256 equality on Windows,
then authorize a fresh test gate and the single experiment. No fix or rerun was
performed here.
