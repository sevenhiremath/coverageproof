"""Regression against genuine owned output; provenance is beside the raw XML."""
import hashlib
import json
from pathlib import Path
from coverageproof.adapters import parse
from coverageproof.domain import State


def test_owned_nmap_recording_is_preserved_and_interpretable():
    root=Path(__file__).resolve().parents[1]/'samples/recorded-nmap'
    raw=(root/'nmap.xml').read_bytes();manifest=json.loads((root/'manifest.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==manifest['sha256']
    assert manifest['source']=='recorded_genuine' and manifest['exit_status']==0
    rows=parse('nmap',raw)
    assert len(rows)==1 and rows[0].target=='127.0.0.1'
    assert rows[0].check=='tcp-port:8765' and rows[0].outcome==State.FINDING
    assert rows[0].issue_class is None  # Service discovery never invents a vulnerability.
    assert rows[0].observed_at=='1793635273'
