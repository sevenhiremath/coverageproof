# Recorded real-browser test

Source: https://github.com/sevenhiremath/coverageproof/actions/runs/41488081788 . Head commit e5ad35ebe44d3034989ac94c8a86aee23b75274f, tested merge ref f2da719bcf9b0a14094e46b1246eb957945159bd. Chromium 156.0.8078.4 ran against our owned loopback app/fixture with external networking disabled.

The screenshots are preserved browser captures. Before follow-up: one unanswered declared admin check, one issue candidate. After the approved HTTP follow-up: zero unanswered declared checks, still one issue candidate. That is coverage of two stated response-header conditions, not a claim that the app is secure. The separate synthetic report-review test then adds another declared check to invalidate its test draft; summary.json therefore ends with a new unattempted check.

Planning was labeled development mode; report prose used a synthetic provider to test UI review binding. No live model or native web scanner ran in this browser test. This is reproducible test evidence, not the final submission demonstration. Desktop and mobile screenshots and downloaded report output were inspected; no page errors or mobile horizontal overflow were reported. Later PDF font embedding changes are verified separately.
