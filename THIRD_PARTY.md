# Dependencies and reuse review

No PentestGPT, DefectDojo, Nuclei, Nikto or other reference-project implementation is vendored/copied in this checkpoint. The application uses mature dependencies rather than recreating HTTP, XML parsing, validation, rendering or PDF layout.

| Runtime dependency | License | Role |
|---|---|---|
| FastAPI | MIT | HTTP application |
| Starlette | BSD-3-Clause | ASGI framework |
| Pydantic | MIT | Structured validation |
| Jinja2 / MarkupSafe | BSD-3-Clause | Autoescaped templates |
| HTTPX / HTTPCore / AnyIO | BSD-3-Clause / BSD-3-Clause / MIT | Restricted HTTP client |
| defusedxml | PSF | XML entity protection |
| ReportLab | BSD | PDF layout |
| Uvicorn | BSD-3-Clause | Local server |
| python-multipart | Apache-2.0 | Upload parsing |
| pytest / pypdf (development) | MIT / BSD-3-Clause | Tests and PDF validation |

Installed distribution license metadata is captured in `docs/dependency-licenses.json`. Preserve dependency copyright/license notices in redistributed environments. Scanner tools are not bundled. Nmap uses its own NPSL, Nikto scanner code is GPL-3.0 and its databases have separate terms, ZAP is Apache-2.0: review distribution/data restrictions before bundling or publishing tool images.

Relevant references inspected, not executed:
- DefectDojo `dojo/tools/nikto/parser.py`: parser dispatch by format and explicit output-version handling; BSD-3-Clause project.
- Nikto `program/plugins/nikto_report_json.plugin`: format producer fields and multi-host array; GPL-3.0-only file. Parser is independently written against the data format.
- Nmap XML documentation; OWASP ZAP traditional JSON documentation.
- PentestGPT (MIT) and Nuclei (MIT): public architecture/result-schema references from prior research; neither is integrated. The product does not claim their functionality as its own.

Other supplied repositories (Arjun, Dalfox, reconFTW, tomnomnom and individual-builder profiles) are optional background, not incorporated dependencies. No licenses are inferred for code that has not been selected for use.
