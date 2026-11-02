# Integration truth table

Native imports are permitted by PS-1 p3 §4 and p5 §6. This is an engineering checkpoint, not a claim that all mandatory integrations have passed genuine-output verification.

| Tool | Status | Supported format/version | Verification | Limitations |
|---|---|---|---|---|
| Nmap | Import-only (parser implemented) | XML xmloutputversion 1.04 / 1.05, scanner=nmap | Handwritten schema fixtures | Explicit TCP port records only; no extraports inference, NSE or vulnerability inference; genuine output pending |
| Nikto | Import-only (parser implemented) | Current multi-host JSON array: host/ip/port/start_time/end_time/vulnerabilities | Current upstream exporter inspected; schema fixtures | Legacy objects rejected; exporter lacks version field, cannot attest tool version; genuine output pending; no negative coverage inferred |
| OWASP ZAP | Import-only (parser implemented) | ZAP 2.x traditional JSON, site[]/alerts[]/instances[] | Official sample schema inspected; schema fixtures | Dev/unknown versions rejected; alert exports do not prove traversal/rule completion; genuine output pending |
| Nessus | Unsupported | None | No adapter | No commercial availability claimed |
| OpenVAS / Greenbone | Planned | None implemented | None | Outside baseline |
| Burp Suite | Unsupported | None | No adapter | Licensing/API availability not assumed |
| Metasploit | Unsupported | None | No adapter | No autonomous or active exploitation runner |

Additional check: bounded HTTP GET tests one X-Content-Type-Options condition. This is a working live check, **not** one of the three named-tool integrations. It never follows redirects; literal-IP scope only; unknown/non-2xx result remains inconclusive.

Sources inspected 2026-11-02:
- https://nmap.org/book/output-formats-xml-output.html
- https://github.com/sullo/nikto/blob/master/program/plugins/nikto_report_json.plugin (default-branch source fetched through GitHub contents API)
- https://www.zaproxy.org/docs/desktop/addons/report-generation/report-traditional-json/

Declare exact per-target checks before importing. The importer preserves the entire raw artifact and hash. Only matching declared check observations affect the current finding/coverage view. An unmatched endpoint remains in raw evidence, not silently counted as covered. Improving the unmatched-observation review is pending.
