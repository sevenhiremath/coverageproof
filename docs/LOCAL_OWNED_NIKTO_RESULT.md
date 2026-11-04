# Owned Nikto recording — November 4, 2026

Source: `test/owned-web-recording`, requested commit
`8af8cad4ed3238d36c6a011053b9c4746e5d1f6e`.
Fresh worktree/notes branch `local/owned-nikto-recording`. Reviewed
scripts/record_owned_web.py, the fixture/Dockerfile and WEB_CHECK_PLAN.md.
Previous evidence was preserved. No source or assertions were changed.

## Result: scanner ran once, structured export unavailable

Tests: **131 passed, 1 warning in 12.71s**; whole test command 13.9210469 seconds.
The warning is the existing Starlette/httpx deprecation.
Built the self-owned coverageproof-fixture image and pulled official Nikto 2.6.1.
Official ZAP stable preparation was still downloading when Nikto recording failed;
the foreground pull was cancelled. ZAP image readiness is not claimed, and no
ZAP process or scan was run.

The authorized Nikto invocation was the fixed current recording script's command:

```text
/opt/nikto/nikto.pl -h http://127.0.0.1:8765/ -Tuning 1 -maxtime 60 -timeout 3 -nointeractive -Format json -output /tmp/results.json
```

This differs from the older headers-only WEB_CHECK_PLAN.md command. It is a
Tuning 1 run against the dedicated owned fixture, not evidence of a headers-only
execution. The exact Docker command, image ID and namespace are in the private
unmodified recording manifest. No other target was supplied.

Nikto console reports **2569 requests, 0 errors, 5 items, one host tested** in
3 seconds. These are tool-reported console counts, not verified application
findings or coverage claims. It also printed an update/submission prompt and
`ERROR: Failed to check for updates:`. No prompt was answered. There was no
external route; this output does not demonstrate a successful external contact.

The shell recorded Nikto exit status **0**. However, Docker copy failed:

```text
Error response from daemon: Could not find the file /tmp/results.json in container cp-web-tool-5c8e1f9dfb
RuntimeError: Raw export unavailable; preserve diagnostics and stop
```

Recording wrapper exit: **1**. Start 2026-11-04 00:23:07.443426 UTC
(05:53:07.443426 IST); end 00:23:19.081998 UTC (05:53:19.081998 IST).
Wall duration: **11.638583 seconds**. Scanner console start/end: 00:23:14–00:23:17
UTC. The script's raw manifest retains status `running` after this exception;
it is not a success indication. The wrapper timing and exception establish failure.

No results.json was retrieved. Native parsing, import.sqlite creation and import
assertions were **not reached**. There is no structured-artifact hash or verified
import to report. Stdout, stderr, copy error, command/timing and containment data
are preserved with their own hashes. No JSON was reconstructed from console text.

## Containment and versions

Nikto version command (no target) reported **2.6.1 (LW 2.5)**. Official image digest:
`ghcr.io/sullo/nikto@sha256:f65dd97be358e8260d97a00e784c05c5f37d2ed69b9a9611b14d3889c2b54efa`.

Before scanning, a disposable preflight verified the same fixture configuration.
The actual recording containers were also inspected and probed during this run:

- Fixture non-root UID 10001; tool non-root UID 100.
- Fixture network mode none; tool shares only that fixture's namespace.
- Only lo interface and no IPv4 routes in both actual runtime probes.
- CapEff zero, NoNewPrivs 1, Seccomp 2 in both runtime probes.
- Read-only root filesystems, no privileged mode, host binds, Docker socket or
  published ports. Tool scratch paths are bounded tmpfs mounts.
- Each container limited to 1 GiB RAM, 2 CPUs, 256 PIDs.

The recording script removed its own two containers in finally. The preflight
container was removed separately. No unrelated Docker networks or containers
were changed. Loopback belongs to this dedicated network-none namespace, not the
host's services. Scope is self-owned development, not organizer authorization.

## Evidence and smallest next step

Private bundle preserves unedited console streams, scanner manifest, copy error,
wrapper traceback/timing, actual fixture/tool inspections and runtime probes,
preflight version/commands, fixture build/tool pull logs, image IDs/digests,
source hashes and an exact-byte archive manifest. Only these reviewed notes are
published. No API key or model was used; Ollama remained stopped.

Next review should determine why the official exporter did not produce the
requested file and why the current command attempted its update path. Inspecting
the exporter/configuration without target traffic is preferable to another scan:
it can establish report naming and scratch requirements without repeating active
requests. An immediate rerun is an alternative but may repeat this failure and
is not authorized by this result. Diagnostic work can still miss runtime-only
behavior; any corrected bounded run should verify exact export bytes, hash and
import assertions. No retry, command fix, assertion change or ZAP run occurred.
