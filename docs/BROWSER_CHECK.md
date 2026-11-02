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
