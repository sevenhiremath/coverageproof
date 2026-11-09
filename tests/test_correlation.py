"""Synthetic unit cases for conservative grouping and attributed risk, not scanner recordings."""
from io import BytesIO
import json
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from coverageproof.app import create_app
from coverageproof.correlation import correlate
from coverageproof.domain import Action, Receipt, State
from coverageproof.planner import model_context
from coverageproof.report import generate


def row(id, issue, tool='zap', target='http://127.0.0.1:8765/admin',outcome=State.FINDING,severity='low',check='web-alerts'):
    return {'id':id,'artifact':'artifact-'+id,'tool':tool,'receipt':Receipt(target=target,check=check,outcome=outcome,detail='Synthetic correlation observation',source_ref='/test/'+id,issue_class=issue,title='Unit fixture title',severity=severity,observed_at='2026-11-02T00:00:00Z')}


def test_known_cross_tool_condition_groups_without_losing_sources():
    rows=[row('a','zap:10021:GET:'),row('b','header:x-content-type-options',tool='http',check='header-nosniff')]
    cases=correlate(rows)
    assert len(cases)==1
    assert cases[0]['source_tools']==['zap','http']
    assert len(cases[0]['source_observations'])==2
    assert {e['observation'] for e in cases[0]['evidence']}=={'a','b'}
    assert cases[0]['issue_class']=='header:x-content-type-options'


def test_nikto_shared_plugin_id_keeps_distinct_conditions_and_duplicate_sources():
    headers=['content-security-policy','x-content-type-options','permissions-policy',
             'referrer-policy','strict-transport-security']
    rows=[]
    for index, header in enumerate(headers):
        item=row(str(index),'nikto:013587',tool='nikto',check='web-server')
        item['receipt']=item['receipt'].model_copy(update={'detail':f'Suggested security header missing: {header}.'})
        rows.append(item)
    duplicate=row('duplicate','nikto:013587',tool='nikto',check='web-server')
    duplicate['receipt']=duplicate['receipt'].model_copy(update={'detail':rows[0]['receipt'].detail})
    cases=correlate(rows+[duplicate])
    assert len(cases)==5
    assert sum(len(c['evidence']) for c in cases)==6
    assert len(next(c for c in cases if c['source_observations'][0]['id']=='0')['evidence'])==2
    assert all(c['source_issue_classes']==['nikto:013587'] for c in cases)
    assert {c['id'] for c in cases}=={c['id'] for c in correlate(list(reversed(rows+[duplicate])))}


@pytest.mark.parametrize('target',['http://127.0.0.2:8765/admin','http://127.0.0.1:8766/admin','http://127.0.0.1:8765/other','http://127.0.0.1:8765/admin?role=other','https://127.0.0.1:8765/admin'])
def test_different_assets_or_response_locations_stay_separate(target):
    assert len(correlate([row('a','zap:10021:GET:'),row('b','header:x-content-type-options',tool='http',target=target,check='header-nosniff')]))==2


@pytest.mark.parametrize('issue',['zap:10021:POST:','zap:10021:GET:parameter','zap:99999:GET:','nikto:unknown-rule'])
def test_unknown_rules_methods_and_parameters_are_not_merged_by_title(issue):
    assert len(correlate([row('a',issue),row('b','header:x-content-type-options',tool='http',check='header-nosniff')]))==2


def test_negative_observation_contradicts_but_does_not_create_issue():
    negative=row('n',None,tool='http',outcome=State.NOT_OBSERVED,check='header-nosniff',severity='unknown')
    assert correlate([negative])==[]
    f=correlate([row('a','zap:10021:GET:'),negative])[0]
    assert f['validation_status']=='conflicting_observations'
    assert len(f['evidence'])==2
    assert f['severity']=='low'


def test_severity_disagreement_preserved_regardless_of_import_order():
    rows=[row('a','zap:999:GET:',severity='low'),row('b','zap:999:GET:',severity='high')]
    for source in [rows,list(reversed(rows))]:
        f=correlate(source)[0]
        assert f['severity']=='high'
        assert f['severity_disagreement'] is True
        assert set(f['source_severities'])=={'low','high'}


def add_receipt(store,assessment,target,severity):
    c=store.add_check(assessment,Action(check='header-nosniff',target=target,scope_revision=1))
    attempt,_,_=store.claim(c,store.approve(c,'Unit analyst'))
    r=Receipt(target=target,check='header-nosniff',outcome=State.FINDING,detail='Synthetic direct-check test only',source_ref='test',issue_class='header:x-content-type-options',title='Header unit fixture',severity=severity)
    store.finish(attempt,'completed','Synthetic result',b'unit fixture',r)


def test_risk_order_uses_explicit_inputs_without_invented_score(store,scope):
    a=store.create('Risk-order unit test',scope)
    for path in ['/a','/z']:add_receipt(store,a,'http://127.0.0.1:8765'+path,'low')
    snap=store.snapshot(a);last=snap['findings'][1]
    store.set_risk_context(a,last['id'],'internal_per_owner','high','not_assessed',[],'Owner describes this as a high-impact internal asset.','Analyst')
    snap=store.snapshot(a)
    assert snap['findings'][0]['id']==last['id']
    assert snap['findings'][0]['cvss'] is None
    assert snap['findings'][0]['risk_explanation']['asset_impact']=='high'
    assert snap['findings'][1]['risk_explanation']['exposure']=='unknown'
    assert 'risk_score' not in snap['findings'][0]
    assert snap['events'][-1]['kind']=='risk_context_recorded'


def test_risk_validation_requires_real_finding_evidence(store,scope):
    a=store.create('Validate context refs',scope);add_receipt(store,a,'http://127.0.0.1:8765/','low')
    f=store.snapshot(a)['findings'][0]
    for refs in [[],['invented-observation']]:
        with pytest.raises(ValueError):store.set_risk_context(a,f['id'],'lab_only','low','analyst_validated',refs,'This cannot be accepted without valid references.','Analyst')
    store.set_risk_context(a,f['id'],'lab_only','low','analyst_validated',[f['evidence'][0]['observation']],'Analyst-declared unit test; not real exploit validation.','Analyst')
    assert store.snapshot(a)['findings'][0]['risk_context']['exploitability']=='analyst_validated'
    assert not store.snapshot(a)['checks'][0]['attempts'][0]['status']=='running'
    other=store.create('Other assessment',scope)
    with pytest.raises(KeyError):store.set_risk_context(other,f['id'],'unknown','unknown','not_assessed',[],'Do not apply context across assessments.','Analyst')


def test_context_is_displayed_in_ui_pdf_and_model_input(store,scope):
    a=store.create('Risk review workflow',scope);add_receipt(store,a,'http://127.0.0.1:8765/','low');f=store.snapshot(a)['findings'][0]
    with TestClient(create_app(store.path)) as client:
        r=client.post(f'/assessments/{a}/findings/{f["id"]}/risk',data={'exposure':'lab_only','asset_impact':'low','exploitability':'not_assessed','evidence_ids':'','note':'This is a development fixture with no established business impact.','actor':'Unit analyst'})
        assert r.status_code==200
        assert 'Why this risk priority?' in r.text
        assert 'development fixture with no established business impact' in r.text
        assert 'Why were these observations grouped?' in r.text
    snap=store.snapshot(a)
    assert model_context(snap)['finding_cases'][0]['risk_explanation']['exposure']=='lab_only'
    text='\n'.join(page.extract_text() for page in PdfReader(BytesIO(generate(store,a))).pages)
    assert 'lab_only' in text and 'Source severity first' in text
    assert 'development fixture with no established business impact' in ' '.join(text.split())


def test_nikto_import_keeps_methods_separate_and_preserves_native_bytes(store,scope):
    a=store.create('Synthetic Nikto method regression',scope)
    store.add_check(a,Action(check='web-server',target='http://127.0.0.1:8765/',scope_revision=1))
    records=[{'id':'013587','url':'/','msg':'Same synthetic condition','method':m} for m in ['GET','POST']]
    records.append({'id':'013587','url':'/','msg':'Same synthetic condition'})
    raw=json.dumps([{'host':'127.0.0.1','ip':'127.0.0.1','port':'8765','start_time':'test','end_time':'test','vulnerabilities':records}]).encode()
    store.ingest(a,'nikto',raw)
    snap=store.snapshot(a)
    assert len(snap['findings'])==3
    assert {f['source_observations'][0]['http_method'] for f in snap['findings']}=={'GET','POST',None}
    assert all(f['source_issue_classes']==['nikto:013587'] for f in snap['findings'])
    from hashlib import sha256
    assert snap['artifacts'][0]['sha256']==sha256(raw).hexdigest()
