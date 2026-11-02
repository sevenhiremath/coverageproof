# Paste this task into the local ChatGPT app

Continue CoverageProof from https://github.com/sevenhiremath/coverageproof . Online Work handles application changes. Your task is genuine local runtime validation. Online GitHub Actions now also runs the isolated backend tests and a single owned Nmap recording; inspect its actual result before duplicating work. Nikto/ZAP and actual Ollama/browser checks remain pending. Docker and the 33 old checkpoint tests were already verified; do not repeat hardware inspection, tune the machine or download another AI model. Read current README, STATUS, INTEGRATIONS, DECISIONS and this file. Preserve the original extraction and unrelated Docker resources.

## 1. Get the current source

Use a fresh folder, not the old bundle branch. In PowerShell:

```powershell
git clone https://github.com/sevenhiremath/coverageproof.git coverageproof-current
cd coverageproof-current
git switch -c local/runtime-checks
git status --short
git rev-parse HEAD
docker build -f Dockerfile.tests -t coverageproof-tests .
docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --memory 1g --cpus 2 --pids-limit 128 coverageproof-tests
```

Expected: current test suite passes; record actual count/output and commit. The earlier 33-test result does not validate current source.

## 2. Build and verify the isolated owned fixture

These setup commands start only our benign fixture, not a scanner:

```powershell
docker build -f local-lab/Dockerfile.fixture -t coverageproof-fixture .
docker build -f local-lab/Dockerfile.nmap -t coverageproof-nmap .
docker run -d --name coverageproof-fixture --network none --cap-drop ALL --security-opt no-new-privileges --read-only --memory 128m --cpus 1 --pids-limit 32 coverageproof-fixture
docker inspect coverageproof-fixture
docker exec coverageproof-fixture python -c "import socket,pathlib; print(socket.if_nameindex()); print(pathlib.Path('/proc/net/route').read_text()); print(pathlib.Path('/proc/self/status').read_text()); print(pathlib.Path('/proc/mounts').read_text())"
docker exec coverageproof-fixture python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8765/admin', timeout=2); print(r.status, r.headers.get('X-Content-Type-Options'))"
```

Expected: only loopback, no external/default route, no published ports, no host bind mounts, non-root process, no effective capabilities, no privilege escalation, read-only root filesystem; fixture returns 200 and nosniff. Record observed output rather than assuming containment. Check attempted external and unrelated-container connectivity fails using short timeouts from this namespace; do not probe third-party service applications. Stop if isolation is not verified. Reuse neither an existing unrelated container nor an existing network. If our container name already exists, inspect it and choose a new task-specific name; do not delete unknown containers.

## 3. Prepare exact scanner commands for approval

Runtime topology: scanner joins only `--network container:coverageproof-fixture`, sharing the fixture's network-none loopback namespace. No host networking, privileged mode, Docker socket, host mounts, network connect or vulnerable-service port publishing. Setup may download images; scanner runtime must lack external egress.

- Nmap image is built above from Debian packages. Inspect `--version` and image ID. Proposed bounded scan: `-sT -Pn -n -p 8765 --max-retries 1 --host-timeout 30s -oX /tmp/nmap.xml 127.0.0.1` with runtime timeout and stdout/stderr capture.
- Nikto: use the official Sullo image after verifying registry/tag, digest, version and entrypoint. Limit target to `http://127.0.0.1:8765/`, scan time and tuning as supported by the installed release; request multi-host native JSON. Do not use exploit/credential modes. Confirm actual flags before presenting the final command.
- ZAP: use official stable image after recording digest/version. Passive baseline against that same URL only; bounded spider duration and total runtime; native traditional JSON. No active attack scan. Fixture has only same-origin links. Confirm the installed script/report options.

Use resource limits, dropped capabilities/no-new-privileges, bounded output and timeouts. Use writable temporary container storage only where the tool requires it. Copy raw outputs out with docker cp; never rewrite an output to satisfy a parser. Inspect the scanner container's actual namespace/privileges too.

Return the exact installed-version commands, target, scope, options and limits for required approval BEFORE active web assessment. Setup authorization does not authorize arbitrary later offensive validation. Do not stop after only recommending Docker; finish this concrete preparation first. After approval, collect genuine outputs and import them through the app; errors remain failures, missing alerts remain uncertain. Do not fabricate a vulnerability to improve the demo.

## 4. Verify the existing local model and browser

No paid API key or subscription automation. Use the already-installed qwen3.5:9b model; no new downloads or hardware tuning. Run the app natively in a separate Python 3.11+ virtual environment (Python 3.14 was reported installed; use it if dependency install succeeds). Do not replace system Python. In PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e '.[test]'
$env:COVERAGEPROOF_PROVIDER='ollama'
$env:OLLAMA_MODEL='qwen3.5:9b'
$env:COVERAGEPROOF_DB='data/local-model-check.sqlite'
.\.venv\Scripts\python -m uvicorn coverageproof.app:app --host 127.0.0.1 --port 8000
```

Keep scanner isolation separate from the native app/model check. The app's fixed Ollama endpoint is loopback. If a current model runtime is unavailable, return the exact error; do not silently use development rules. In browser, create a self-owned scope and natural-language network/web request, generate an initial model plan, then test follow-up planning using genuine stored evidence. Verify rationale, relevant rejected alternatives, drawback, real observation IDs, policy outcome, approval and report. Use the report-draft button to obtain actual model prose, inspect its citations, accept it as analyst, then confirm only the current accepted draft appears in the PDF. New evidence must invalidate it. Record wall-clock elapsed time for each call, actual model/runtime versions, validated proposal or actual rejection. No credentials/environment dumps. Approval is collected through the app for supported live HTTP actions. Do not claim Docker fixture port 8765 is reachable from the host; it intentionally is not.

For a host-browser HTTP follow-up, use a separately identified self-owned loopback development fixture (`python local-lab/fixture.py`) with explicit app scope; label it development only, not isolated scanner evaluation. Never scan unrelated host services. Review the PDF in a real viewer, check all pages, long evidence text, links, state labels and download behavior. Record browser/version and screenshots without personal data.

## 5. Return a small reviewable result

Commit setup corrections only under local-lab/ and concise validation notes under docs/ on your branch. Use simple messages such as 'Record the local model check'. Do not edit coverageproof/ or parser contracts without coordinating. Push normally; no force push, no merges over concurrent changes.

Return the branch/commit and an ignored scanner-artifacts/ bundle (share privately first). Include genuine raw Nmap XML/Nikto JSON/ZAP JSON, stdout/stderr, manifest.json, lab-scope.json, containment evidence, exact commands, versions/digests, UTC start/end timestamps, exit statuses, hashes and limitations. Label every source as recorded_genuine, live_execution, unit_fixture or synthetic_failure_injection accurately. No API keys or unrelated host data. Share only owned non-sensitive samples publicly after inspection. Also return actual Ollama decisions/errors/timings, browser/PDF check results and reproducible problems. Screenshot-only or a capability report is insufficient.

Organizer environment authorization is separate and still missing. No third-party targets, final submission, Drive publishing, invitations or organizer messages.
