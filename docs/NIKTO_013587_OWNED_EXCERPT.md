# Owned Nikto 013587 source excerpt

Sanitized from the accepted genuine Nikto recording on source commit
`6d55609d8053821c2b86b7945bc5814ed71c23f3`, notes commit `efa03a7`.
Native artifact SHA256:
`47e311a5d2fa3a1649aed40504ac355b9693b874d633c33e36381fcb2eaffc4d`.
This is the dedicated network-none development fixture, not host services or
organizer infrastructure. All rows have native source ID **013587**, method
**GET**, native URL **/**, resolved URL **http://127.0.0.1:8765/**.

| Native source pointer | Exact native message |
|---|---|
| /0/vulnerabilities/0 | Suggested security header missing: content-security-policy. |
| /0/vulnerabilities/1 | Suggested security header missing: x-content-type-options. |
| /0/vulnerabilities/2 | Suggested security header missing: permissions-policy. |
| /0/vulnerabilities/3 | Suggested security header missing: referrer-policy. |
| /0/vulnerabilities/4 | Suggested security header missing: strict-transport-security. |

The parser assigns all five `issue_class=nikto:013587`. The accepted import
therefore has one candidate with five distinct source details. These are different
named header conditions even though the native ID, method and URL match.
The original message and source pointer must remain available if correlation
adds a header-specific distinction. The nosniff record alone corresponds to
that specific header condition; do not infer that every 013587 message is nosniff.
No raw output was edited, and this task makes no parser/correlation changes.
