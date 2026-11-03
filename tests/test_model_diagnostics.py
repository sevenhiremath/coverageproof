"""Synthetic provider responses test the real rejection and private recording path."""
import hashlib
from io import BytesIO
import json
import httpx
import pytest
from pypdf import PdfReader
from coverageproof.domain import Action, CHECKS
from coverageproof.planner import model_plan_schema, plan
from coverageproof.narrative import draft_report
from coverageproof.report import generate
from coverageproof.model_diagnostics import export_calls


def proposal(check='header-nosniff'):
    return {'mode':'model','explanation':'The declared admin response still needs a bounded observation.',
        'checks':[{'action':{'check':check,'target':'http://127.0.0.1:8765/admin','scope_revision':1},
            'rationale':'Unit-only-private-note: inspect the unanswered declared condition.',
            'evidence_ids':[],'alternatives':[{'tool':'nikto','reason_not_chosen':'A broader server scan is unnecessary for this response condition.'}],
            'drawback':'Only one response is assessed; other conditions stay unknown.'}]}


def mocked(monkeypatch,content,**extra):
    captured=[];actual=httpx.Client
    def respond(request):
        captured.append(request)
        return httpx.Response(200,json=dict(done=True,message={'content':content,'thinking':'Private thinking is not persisted'},**extra))
    monkeypatch.setattr(httpx,'Client',lambda **kw:actual(transport=httpx.MockTransport(respond),**kw))
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','ollama')
    return captured


def calls(store,a):
    with store.tx() as db:
        return [dict(r,metadata=json.loads(r['metadata'])) for r in db.execute('SELECT * FROM model_calls WHERE assessment=?',(a,))]


def test_registered_names_are_in_transmitted_schema(store,scope,monkeypatch):
    a=store.create('Assess admin response headers',scope)
    requests=mocked(monkeypatch,json.dumps(proposal()))
    plan(store,a)
    body=json.loads(requests[0].content)
    assert set(body['format']['$defs']['Action']['properties']['check']['enum'])==set(CHECKS)
    assert body['format']['properties']['mode']['const']=='model'
    assert 'Output JSON schema:' in body['messages'][0]['content']
    assert 'Never invent a no-action check' in body['messages'][0]['content']
    c=calls(store,a)[0]
    assert c['metadata']['outcome']=='accepted' and c['metadata']['elapsed_ms']>=0
    assert not store.snapshot(a)['approvals'] and not store.snapshot(a)['artifacts']


@pytest.mark.parametrize('check',['no_additional_action','run_nikto','shell'])
def test_unknown_action_is_retained_privately_without_closing_gap(store,scope,monkeypatch,check):
    a=store.create('Inspect the declared admin check',scope)
    store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1))
    raw=json.dumps(proposal(check));mocked(monkeypatch,raw)
    with pytest.raises(ValueError) as error:plan(store,a)
    assert 'Unit-only-private-note' not in str(error.value)
    saved=calls(store,a)[0];meta=saved['metadata']
    assert saved['raw_output']==raw.encode()
    assert meta['output_sha256']==hashlib.sha256(raw.encode()).hexdigest()
    assert meta['output_complete'] and meta['outcome']=='rejected'
    assert any(e['type']=='extra_forbidden' for e in meta['validation_errors'])
    assert 'Private thinking' not in saved['raw_output'].decode()
    snap=store.snapshot(a)
    assert len(snap['checks'])==1 and snap['checks'][0]['state']=='unattempted'
    assert not snap['approvals'] and not snap['artifacts']
    assert 'Unit-only-private-note' not in json.dumps(snap)
    text=' '.join(p.extract_text() for p in PdfReader(BytesIO(generate(store,a))).pages)
    assert 'Unit-only-private-note' not in text
    assert snap['events'][-1]['kind']=='planning_failed'


def test_semantic_citation_rejection_keeps_original_response(store,scope,monkeypatch):
    a=store.create('Cite only stored observations',scope)
    p=proposal();p['checks'][0]['evidence_ids']=['invented-id'];raw=json.dumps(p)
    mocked(monkeypatch,raw)
    with pytest.raises(ValueError,match='nonexistent'):plan(store,a)
    assert calls(store,a)[0]['raw_output']==raw.encode()
    assert not store.snapshot(a)['checks']


def test_empty_check_list_does_not_close_unattempted_check(store,scope,monkeypatch):
    a=store.create('Still an unanswered header check',scope)
    store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1))
    mocked(monkeypatch,json.dumps({'mode':'model','explanation':'The model declined to propose a useful action in this unit fixture.','selections':[]}))
    assert plan(store,a).checks==[]
    assert store.snapshot(a)['checks'][0]['state']=='unattempted'


def test_incomplete_output_is_recorded_but_never_added(store,scope,monkeypatch):
    a=store.create('Test incomplete provider reply',scope);raw=json.dumps(proposal())
    mocked(monkeypatch,raw,done_reason='length',total_duration=123456789)
    with pytest.raises(ValueError,match='incomplete'):plan(store,a)
    c=calls(store,a)[0]
    assert c['raw_output']==raw.encode() and not c['metadata']['output_complete']
    assert c['metadata']['total_duration']==123456789
    assert not store.snapshot(a)['checks']


def test_report_draft_rejection_records_call_without_prose_in_report(store,scope,monkeypatch):
    a=store.create('Draft from declared checks',scope)
    store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1))
    raw=json.dumps({'mode':'model','executive_summary':[{'text':'Unit-only-private-note: invented report evidence must be rejected.','check_ids':['invented-check'],'evidence_ids':[]}],
        'limitations':[{'text':'This rejected unit draft must not enter the PDF.','check_ids':['invented-check'],'evidence_ids':[]}]})
    mocked(monkeypatch,raw)
    with pytest.raises(ValueError):draft_report(store,a)
    c=calls(store,a)[0]
    assert c['purpose']=='report_draft' and c['raw_output']==raw.encode()
    assert not store.snapshot(a)['report_draft']


def test_private_export_preserves_exact_bytes_and_refuses_overwrite(store,scope,monkeypatch,tmp_path):
    a=store.create('Private export fixture',scope);raw=json.dumps(proposal('unknown-unit-check'))
    mocked(monkeypatch,raw)
    with pytest.raises(ValueError):plan(store,a)
    out=tmp_path/'private'
    assert export_calls(store.path,out,a)==1
    entry=json.loads((out/'manifest.json').read_text())[0]
    assert (out/entry['output_file']).read_bytes()==raw.encode()
    with pytest.raises(FileExistsError):export_calls(store.path,out,a)


def test_timeout_has_timing_but_no_fake_model_output(store,scope,monkeypatch):
    a=store.create('Provider timeout fixture',scope);actual=httpx.Client
    def respond(request):raise httpx.ReadTimeout('A unit timeout, not a real model run')
    monkeypatch.setattr(httpx,'Client',lambda **kw:actual(transport=httpx.MockTransport(respond),**kw))
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','ollama')
    with pytest.raises(ValueError,match='ReadTimeout'):plan(store,a)
    c=calls(store,a)[0]
    assert c['metadata']['elapsed_ms']>=0 and c['metadata']['error_type']=='ReadTimeout'
    assert c['raw_output']==b'' and not c['metadata']['output_complete']
    assert not store.snapshot(a)['checks']


def test_response_limit_is_bounded_and_not_interpreted(store,scope,monkeypatch):
    a=store.create('Oversized model body fixture',scope)
    mocked(monkeypatch,'x'*300000)
    with pytest.raises(ValueError,match='256 KiB'):plan(store,a)
    c=calls(store,a)[0]
    assert c['metadata']['captured_response_truncated'] and c['raw_output']==b''
    assert c['metadata']['output_size']==0 and not store.snapshot(a)['checks']


def test_private_values_in_extra_field_names_do_not_leak(store,scope,monkeypatch):
    a=store.create('Rejected extra model field',scope)
    p=proposal();p['unit-secret-extra-field']='unit-secret-value';mocked(monkeypatch,json.dumps(p))
    with pytest.raises(ValueError) as e:plan(store,a)
    assert 'unit-secret' not in str(e.value)
    assert 'unit-secret' not in json.dumps(store.snapshot(a))
    assert calls(store,a)[0]['raw_output']==json.dumps(p).encode()


def test_malformed_envelope_is_not_persisted_as_valid_output(store,scope,monkeypatch):
    a=store.create('Malformed envelope fixture',scope);actual=httpx.Client
    monkeypatch.setattr(httpx,'Client',lambda **kw:actual(transport=httpx.MockTransport(lambda r:httpx.Response(200,content=b'{unit-private-envelope')),**kw))
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','ollama')
    with pytest.raises(ValueError,match='unsupported response shape'):plan(store,a)
    c=calls(store,a)[0]
    assert c['raw_output']==b'' and c['metadata']['output_kind']=='provider_envelope'
    assert c['metadata']['captured_response_sha256']==hashlib.sha256(b'{unit-private-envelope').hexdigest()
    assert 'unit-private-envelope' not in json.dumps(store.snapshot(a))


def test_experiment_failure_exports_real_state_without_followup(tmp_path,monkeypatch):
    import runpy
    import sqlite3
    from pathlib import Path
    from coverageproof.planner import OllamaProvider
    script=Path(__file__).resolve().parents[1]/'scripts/experiment.py'
    raw=json.dumps(proposal('no_additional_action'))
    def invalid_response(self,*args):
        self.raw_output=raw.encode()
        self.trace={'provider':'ollama','elapsed_ms':1.25,'output_complete':True,'output_sha256':hashlib.sha256(self.raw_output).hexdigest()}
        return raw
    monkeypatch.setattr(OllamaProvider,'structured',invalid_response)
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','ollama')
    monkeypatch.chdir(tmp_path)
    (tmp_path/'output').mkdir()
    (tmp_path/'output/experiment-summary.json').write_text('{"status":"completed"}')
    with pytest.raises(ValueError,match='failed validation'):runpy.run_path(str(script),run_name='__main__')
    summary=json.loads((tmp_path/'output/experiment-summary.json').read_text())
    assert summary['status']=='failed' and summary['planner_mode'] is None
    a,b=summary['assessment_ids']
    snap=json.loads((tmp_path/'output'/f'{b}.json').read_text())
    assert [c['state'] for c in snap['checks']]==['finding_supported','unattempted']
    assert len(snap['approvals'])==1  # Root fixture check only, no admin follow-up.
    assert sum(len(c['observations']) for c in snap['checks'])==1
    manifest=json.loads((tmp_path/'output'/summary['diagnostics_dir']/b/'manifest.json').read_text())
    assert manifest[0]['metadata']['outcome']=='rejected'
    assert (tmp_path/'output'/summary['diagnostics_dir']/b/manifest[0]['output_file']).read_bytes()==raw.encode()
    assert (tmp_path/'output'/summary['report_file']).read_bytes().startswith(b'%PDF')
