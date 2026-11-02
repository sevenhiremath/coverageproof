# Small local task: obtain genuine native scanner outputs

Online limitation observed: no Docker/Nmap/Nikto/ZAP binaries. `apt-get update` failed with setgroups/seteuid permission errors. Python app and dependencies work online. Do not move project development locally.

First obtain organizer evaluation authorization separately. The task below is only for a self-owned development fixture. It does not authorize scanning anything else.

1. From the repository, run a tiny owned fixture in one terminal:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory tests/fixtures
```

2. If Nmap is already installed on the local machine, in a second terminal:

```bash
mkdir scanner-artifacts
nmap -sT -Pn -n -p 8765 -oX scanner-artifacts/nmap.xml 127.0.0.1
nmap --version
```

Expected: XML with scanner=nmap, explicit TCP/8765 open and a finished run record; no service-vulnerability claim. Return `nmap.xml` and the version output. This is the smallest initial scanner task; it does not require Docker.

3. Nikto and ZAP recordings require installed tool paths, pinned versions and scope-safe invocation. Those commands will be prepared after checking which local runtimes exist; do not paste arbitrary AI-generated scanner commands or scan public targets. Keep Nikto and ZAP imports unverified until those genuine files pass the adapters.

No secrets or organizer credentials should be included in returned artifacts. This directory contains no confidential organizer data.

Update: read LOCAL_HANDOFF.md first. The November 2 isolation requirement supersedes bare-host use of the illustrative commands above for evaluation. Inspect local runtimes before choosing commands; do not run scanners outside an isolated authorized lab.
