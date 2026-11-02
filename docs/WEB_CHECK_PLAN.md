# Proposed owned web checks — approval required before execution

This is a reviewable plan, not an executed scan. The user's requirement is human approval for active/offensive validation. We therefore stop before these web-tool runs and request approval for this exact fixture, images and options. Image preparation/help/version commands ran without target traffic in https://github.com/sevenhiremath/coverageproof/actions/runs/41478631044 . Nikto reports 2.6.1; ZAP reports 2.17.0. ZAP logged an unresolved container-hostname warning under network-none; the version process still returned successfully. This is not a scan success receipt.

## Scope and containment

Only the self-owned local-lab/fixture.py instance created by scripts/record_owned_nmap.py's topology: network-none Docker namespace, literal 127.0.0.1, assessment port 8765, web paths under / only. Only / and /admin are implemented; other paths return 404. The fixture has no external links or credentials. Unknown paths return 404. Internal ZAP API control traffic on loopback port 8080 is scanner control, not an added assessment asset. No service is published to the host.

Before each run, inspect the fixture and scanner: only loopback, no external routes/egress, non-root, no effective capabilities, no-new-privileges, no host mounts/socket, no privileged mode, resource bounds. Images may download during setup, but scanner runtime shares only the fixture's network-none namespace. No host networking or network connect. Stop on failed containment. This authorizes no organizer environment, third-party target or other host service.

## Exact proposed scanner commands

Nikto: only the headers plugin and its native JSON report. No injection, credential, upload, exploit, denial-of-service, mutation or redirect-following options. Image is pinned to the digest observed during preparation. Collect stdout/stderr and exact exit status; enforce a 90-second outer timeout and a 256-KiB console interpretation limit.

```bash
timeout 90 docker run --name coverageproof-nikto --network container:coverageproof-recording-fixture --cap-drop ALL --security-opt no-new-privileges --user nikto --memory 256m --cpus 1 --pids-limit 64 ghcr.io/sullo/nikto@sha256:f65dd97be358e8260d97a00e784c05c5f37d2ed69b9a9611b14d3889c2b54efa -host http://127.0.0.1:8765/ -Plugins headers -maxtime 60s -timeout 5 -Pause 0.1 -nocheck -nointeractive -nolookup -ask no -Format json -output /tmp/nikto.json
docker cp coverageproof-nikto:/tmp/nikto.json output/native-web/nikto.json
```

ZAP: passive baseline with bounded traditional spider; no active attack scan or Ajax/browser spider. Native JSON via the documented -J option and classic baseline path. The fixed Python wrapper only creates its internal report directory and invokes these literal arguments; no model-supplied code or shell. A 512-MiB JVM ceiling fits inside the 1-GiB container bound. Preserve warning exit codes; baseline exit status is not a per-rule negative receipt.

```bash
timeout 180 docker run --name coverageproof-zap --network container:coverageproof-recording-fixture --cap-drop ALL --security-opt no-new-privileges --user zap --memory 1g --cpus 2 --pids-limit 256 ghcr.io/zaproxy/zaproxy@sha256:030d3df57735dacbb83464854758e674dd9ad01d79d12a129a8e58b1fd384238 python3 -c 'import os,subprocess,sys; os.makedirs("/zap/wrk",exist_ok=True); result=subprocess.run(["zap-baseline.py","-t","http://127.0.0.1:8765/","-m","1","-T","2","--autooff","-J","/tmp/zap.json","-z","-Xmx512m"],timeout=150); sys.exit(result.returncode)'
docker cp coverageproof-zap:/tmp/zap.json output/native-web/zap.json
```

Web-tool root filesystems are writable ephemeral container overlays because the tools initialize local settings and reports. No host bind mount is used. This differs from the read-only Nmap/fixture containers; benefit is standard tool compatibility, drawback is writable internal scratch state. Copy reports before removing only the containers created by this task. Do not delete unrelated Docker resources.

## Required recording and interpretation

Record approval identity/reference and this plan's exact source commit, fixture source hash, tool image digests, version, literal arguments, scope, UTC start/end times, stdout/stderr, actual exit status and unedited raw artifact hashes. Preserve setup/timeout failures; never edit reports to make an adapter pass. Stop at 4 MiB raw output and mark oversized output uninterpretable. Import into an assessment for this specific fixture, not a host/organizer scope with the same loopback address.

Validate genuine outputs against the implemented adapters, then add inspected non-sensitive regression samples. Reports remain import-only in the app, not application-executed scans. Missing Nikto/ZAP alerts remain inconclusive; neither proves a complete negative for all rules or routes. A successful run against this small fixture does not validate every version, plugin or vulnerability class.

Alternative: run broad default/active scans or use a large vulnerable image. We chose narrow header/passive checks because they provide genuine supported formats and web coverage with a small scope. Drawback: limited finding variety and no exploitability demonstration. The mandatory contribution is explaining and closing declared assessment gaps, not maximizing alert counts.
