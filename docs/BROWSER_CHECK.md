# Real browser verification online

The local Tabbit launcher failed with CLI_REGISTRATION_UNAVAILABLE. We do not change the user's browser installation. Instead, GitHub Actions can run a versioned official Playwright/Chromium container against our own app and fixture with external networking disabled.

Dockerfile.browser uses Playwright Python 1.64.1 with its matching official browser image. The browser process runs as a non-root user with no Linux capabilities, no new privileges, no host mounts/socket, no published ports and only a network-none loopback interface. Its filesystem is a disposable writable overlay so screenshots/reports survive container exit for docker cp. Private database/profile data stays outside the copied /artifacts directory. Chromium's own sandbox is disabled for this trusted app test; this setup is not offered for arbitrary/untrusted browsing. We do not add SYS_ADMIN or share host IPC.

scripts/check_browser.py uses real Chromium to create a scope and declared checks, approve and execute owned HTTP checks, inspect a proposal, download evidence/PDF, reject an out-of-scope action and check mobile horizontal overflow. The provider for planning is explicitly development mode. Report prose is a labeled synthetic provider to test review and invalidation through the UI. No actual model or native web scanner runs here, and automated review is not presented as human sign-off.

| Choice | Benefit | Alternative / why not now | Drawback |
|---|---|---|---|
| Official versioned browser image | Reproducible real Chromium without changing the local browser | Repair Tabbit: requires changing the user's desktop session | Larger CI image; the workflow must actually pass |
| Isolated owned fixture | Exercises real HTTP/evidence behavior | Public app: no testing authorization and unnecessary variability | Does not establish organizer-lab permission |
| Synthetic report provider in the test process only | Tests buttons, review binding and PDF exclusion reliably | Depend on a live model for every UI regression | Does not validate real AI quality; local model test remains required |
| Screenshots, downloads and summary | Review visible behavior and exact checks performed | HTTP-only checks miss layout and download behavior | Human visual inspection is still needed |

Source: official Docker documentation https://playwright.dev/python/docs/docker . No upstream application code copied. See the actual workflow result and artifact summary before claiming browser verification passed.


The first real run passed in Chromium 156.0.8078.4: https://github.com/sevenhiremath/coverageproof/actions/runs/41487029418 . Desktop and 390-pixel screenshots were inspected; no horizontal overflow or page errors were reported. This is one automated owned-fixture run, not live-model validation. The later unanswered-check summary has a dedicated backend/PDF consistency test and is being rechecked in Chromium.

The workspace now puts unanswered declared checks near the top, with source-state reasons and links to the relevant check. Benefit: analysts can find the missing question without reading every finding. Alternative: show only issue totals or a broad coverage percentage; either can obscure the declared denominator or uncertainty. Drawback: the declared plan still determines what can be called a gap. Not-applicable reviews remain separate from completed conditions. These same counts appear in the backend snapshot and PDF, rather than being independently calculated in the UI.


Visual inspection of the first container PDF showed different text spacing when its unembedded Helvetica was substituted by a viewer. Reports now embed ReportLab's existing Bitstream Vera fonts consistently, including the footer. The font's original copyright/permission table is preserved in the subset and its license is included in LICENSES/. Benefit: portable layout and no OS font installation. Alternative: rely on built-in PDF font substitutions or add OS-specific fonts; both varied between observed environments. Drawback: the selected font does not cover every writing system. The regression checks embedding/notices and PDF state consistency; the changed report is also rendered for inspection.
