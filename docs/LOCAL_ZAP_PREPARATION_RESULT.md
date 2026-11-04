# ZAP preparation stopped — November 4, 2026

Source: exact requested commit
`6d55609d8053821c2b86b7945bc5814ed71c23f3`.
Fresh worktree and notes branch `local/zap-integration-proof`. Accepted Nikto
proof and all prior private evidence/worktrees were preserved. No merge/main
change, model call, Ollama start or application edit occurred.

**ZAP: image preparation incomplete; scanner not run; import unverified.**

Initial image inspection reported:

```text
Error response from daemon: No such image: ghcr.io/zaproxy/zaproxy:stable
```

The earlier cancelled preparation had not produced a runnable image. One new
image preparation command was started for this authorized ZAP task:

```text
docker pull ghcr.io/zaproxy/zaproxy:stable
```

Some layers completed, but the image did not finish. At the user's explicit
direction, the current pull was cancelled. No retry, alternate image/tag or
cached-layer removal was performed. The pull client returned exit 1 following
cancellation, with no additional stderr error. No matching pull client remained.
The log contains layer progress, not a completed image digest or scanner result.

Preparation timing, measured from pull-log creation to cancellation request:

- Log created: 2026-11-04 17:30:18.4837775 IST.
- Last layer-completion output: 17:37:16.1612422 IST.
- Cancellation: 17:51:22.7481627 IST.
- Approximate elapsed: **1264.264 seconds (21 minutes 4 seconds)**.

This is log-lifecycle wall time, not separately instrumented Docker server
download time. The private status file preserves these timestamps and the raw
preparation log. No target traffic, fixture launch, containment probe, ZAP version
process, parser invocation or app import was performed during this task. The
unexecuted verification wrapper/preflight files are not runtime evidence.

## Nikto correlation excerpt delivered

See NIKTO_013587_OWNED_EXCERPT.md for the exact five native messages, source
pointers, common ID, method and URL from the accepted owned recording.
All are GET / at http://127.0.0.1:8765/ with ID 013587, but each names a different
header. The private sanitized JSON additionally maps each native source pointer
to its imported observation/artifact ID. This is extraction from preserved
evidence, not another Nikto run. No scanner output was changed.

The five source observations must remain attributable when online work revises
correlation. The generic native ID alone does not distinguish the five header
conditions. No parser fix is implemented in this notes branch.

## Evidence and remaining blocker

Private bundle: preparation log/status, sanitized source excerpt and an exact-byte
hash manifest. Raw accepted Nikto bundle stays in its original location. Cached
Docker layers remain intact. No Docker-wide cleanup or unrelated resource change.
ZAP needs completed image preparation and a separately continued single owned
recording before any export, containment, parsing or integration success can be
claimed. No automatic retry is scheduled by this note.
