# Genuine owned Nmap recording

Source: GitHub Actions run https://github.com/sevenhiremath/coverageproof/actions/runs/41477132439 , commit 6f2d71ae874a7bf167020c9127d77b12ea5f19f5, November 2, 2026. scripts/record_owned_nmap.py created this self-owned network-none fixture, verified isolation and ran Nmap 7.93 TCP connect on 127.0.0.1:8765 only. No service probes, NSE, credentials or exploitation. XML is preserved byte-for-byte and its SHA256 matches manifest.json. stderr is empty.

The app imported this output successfully in a separate network-none container. It records an explicit open-port observation and zero vulnerability candidates. An open port is discovery; no service-security or vulnerability conclusion follows. These are recorded genuine native outputs, not a synthetic unit fixture, a live app scanner runner or organizer evaluation evidence. Historical timestamps remain historical on reimport. The single sample cannot establish broad version compatibility or performance.
