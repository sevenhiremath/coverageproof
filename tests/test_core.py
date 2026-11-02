import json
from io import BytesIO
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pytest
from pydantic import ValidationError
from pypdf import PdfReader
from fastapi.testclient import TestClient
from coverageproof.domain import Action, Receipt, Scope, State, canonical_target, coverage, validate_scope
from coverageproof.adapters import parse
from coverageproof.planner import Proposal, ProposedCheck, validate_proposal, plan
from coverageproof.runner import execute
from coverageproof.report import generate
from coverageproof.app import create_app


def action(target='http://127.0.0.1:8765/',**kwargs):
    return Action(check='header-nosniff',target=target,scope_revision=1,**kwargs)


def nmap(state='open',reason='syn-ack',ip='127.0.0.1',version='1.05',exit='success'):
    # Handwritten schema fixture: NOT a genuine scanner output or demonstration artifact.
    return f'<nmaprun scanner="nmap" xmloutputversion="{version}"><host endtime="1"><status state="up"/><address addr="{ip}" addrtype="ipv4"/><ports><port protocol="tcp" portid="8765"><state state="{state}" reason="{reason}"/></port></ports></host><runstats><finished exit="{exit}"/></runstats></nmaprun>'.encode()


@pytest.mark.parametrize('target',['http://127.0.0.2:8765/','http://127.0.0.1:22/','http://1.1.1.1:8765/'])
def test_scope_rejects(scope,target):
    with pytest.raises(ValueError): validate_scope(scope,action(target))

@pytest.mark.parametrize('target',['http://localhost:8765/','http://127.0.0.1:8765/../admin','http://user@127.0.0.1:8765/','http://127.0.0.1:8765/%2e','http://127.0.0.1:8765/#x','127.0.0.1;id'])
def test_ambiguous_targets(target):
    with pytest.raises(ValueError): canonical_target(target)


def test_revision_and_exclusion(scope):
    with pytest.raises(ValueError): validate_scope(scope.model_copy(update={'revision':2}),action())
    with pytest.raises(ValueError): validate_scope(scope.model_copy(update={'exclusions':('127.0.0.1/32',)}),action())


def test_approval_binding_one_use(store,scope):
    a=store.create('web assessment',scope); c=store.add_check(a,action()); other=store.add_check(a,action('http://127.0.0.1:8766/'))
    approval=store.approve(c,'Analyst')
    with pytest.raises(ValueError): store.claim(other,approval)
    attempt,_,_=store.claim(c,approval)
    store.finish(attempt,'timeout','Synthetic failure injection')
    with pytest.raises(ValueError): store.claim(c,approval)
    assert store.snapshot(a)['checks'][0]['state']==State.FAILED
    assert any(e['kind']=='execution_denied' for e in store.snapshot(a)['events'])


def test_denials_persist(store,scope):
    a=store.create('test',scope)
    with pytest.raises(ValueError): store.add_check(a,action('http://127.0.0.2:8765/'))
    assert store.snapshot(a)['events'][-1]['kind']=='action_denied'


def test_nmap_receipts():
    assert parse('nmap',nmap())[0].outcome==State.FINDING
    assert parse('nmap',nmap('closed','reset'))[0].outcome==State.NOT_OBSERVED
    assert parse('nmap',nmap('filtered','no-response'))[0].outcome==State.INCONCLUSIVE
    assert parse('nmap',nmap(exit='error'))[0].outcome==State.INCONCLUSIVE
    with pytest.raises(ValueError): parse('nmap',nmap(version='9.9'))
    with pytest.raises(ValueError): parse('nmap',b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>')


def test_import_conflict_and_duplicates(store,scope):
    a=store.create('network',scope)
    c=store.add_check(a,Action(check='tcp-port',target='127.0.0.1',port=8765,scope_revision=1))
    for raw in [nmap(),nmap(),nmap('closed','reset')]: store.ingest(a,'nmap',raw)
    snap=store.snapshot(a)
    assert snap['checks'][0]['state']==State.CONFLICT
    assert len(snap['checks'][0]['observations'])==3
    assert len(snap['artifacts'])==3
    assert snap['findings']==[]  # open TCP service is not a vulnerability


def test_import_atomic_scope(store,scope):
    a=store.create('network',scope)
    with pytest.raises(ValueError): store.ingest(a,'nmap',nmap(ip='192.0.2.1'))
    assert not store.snapshot(a)['artifacts']


def test_no_alert_exports_not_negative():
    nikto=[{'host':'127.0.0.1','ip':'127.0.0.1','port':'8765','start_time':'test','end_time':'test','vulnerabilities':[]}]
    zap={'@version':'2.16.1','site':[{'@name':'http://127.0.0.1:8765/','alerts':[]}]}
    for tool,data in [('nikto',nikto),('zap',zap)]:
        assert parse(tool,json.dumps(data).encode())[0].outcome==State.INCONCLUSIVE


@pytest.mark.parametrize('tool,raw',[('nikto',b'{}'),('nikto',b'[]'),('zap',b'{"@version":"9","site":[]}'),('zap',b'null'),('other',b'{}'),('nmap',b'<broken>'),('zap',b'x'*4194305)])
def test_malformed(tool,raw):
    with pytest.raises(ValueError): parse(tool,raw)


def test_model_evidence_and_action_validation(store,scope):
    a=store.create('web assessment',scope)
    proposal=Proposal(mode='model',explanation='Investigate declared surface.',checks=[ProposedCheck(action=action(),rationale='Inspect this approved endpoint.',evidence_ids=['nonexistent'])])
    with pytest.raises(ValueError): validate_proposal(proposal,store.snapshot(a))
    with pytest.raises(ValidationError): Action(check='shell',target='127.0.0.1',scope_revision=1)
    with pytest.raises(ValidationError): Action(check='header-nosniff',target='http://127.0.0.1:8765/',scope_revision=1,command='id')
    assert plan(store,a).mode=='development'


def test_coverage_states():
    assert coverage([])==State.UNATTEMPTED
    assert coverage([],blocked=True)==State.BLOCKED
    for state in [State.NOT_APPLICABLE,State.FAILED,State.INCONCLUSIVE,State.NOT_OBSERVED]:
        r=Receipt(target='127.0.0.1',check='x',outcome=state,detail='test',source_ref='/x')
        assert coverage([r])==state
        assert coverage([r],stale=True)==State.STALE


def test_http_loop_pdf_and_ui(store,scope,tmp_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            if self.path=='/header': self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(b'Owned development fixture')
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    port=server.server_address[1]
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        s=scope.model_copy(update={'ports':(port,)})
        a=store.create('Assess web response header',s)
        checks=[]
        for path in ['/','/header']:
            c=store.add_check(a,action(f'http://127.0.0.1:{port}{path}'));checks.append(c)
        assert all(c['state']==State.UNATTEMPTED for c in store.snapshot(a)['checks'])
        for c in checks: execute(store,c,store.approve(c,'Test analyst'))
        snap=store.snapshot(a)
        assert {c['state'] for c in snap['checks']}=={State.FINDING,State.NOT_OBSERVED}
        assert len(snap['findings'])==1
        assert all(e['mode']=='live' for e in snap['artifacts'])
        raw=generate(store,a)
        text='\n'.join(p.extract_text() for p in PdfReader(BytesIO(raw)).pages)
        assert 'Executive summary' in text and 'condition_not_observed' in text
        assert snap['findings'][0]['id'] in text
        app=create_app(store.path)
        with TestClient(app) as client:
            assert client.get(f'/assessments/{a}').status_code==200
            assert client.get(f'/api/assessments/{a}').json()['id']==a
            assert client.get(f'/assessments/{a}/report.pdf').content.startswith(b'%PDF')
            assert client.post('/assessments',headers={'Origin':'http://evil.test'}).status_code==403
            assert client.get('/',headers={'Host':'evil.test'}).status_code==403
    finally:
        server.shutdown();server.server_close()


def test_nikto_findings_distinct_assets_and_evidence(store):
    scope=Scope(name='two fixtures',networks=('127.0.0.0/30',),ports=(8765,),authorization_reference='Synthetic two-host parser test only')
    a=store.create('web server assessment',scope)
    data=[]
    for ip in ['127.0.0.1','127.0.0.2']:
        store.add_check(a,Action(check='web-server',target=f'http://{ip}:8765/admin',scope_revision=1))
        data.append({'host':ip,'ip':ip,'port':'8765','start_time':'test','end_time':'test','vulnerabilities':[{'id':'123','url':'/admin','msg':'Same issue title','method':'GET'}]})
    for _ in range(2): store.ingest(a,'nikto',json.dumps(data).encode())
    snap=store.snapshot(a)
    assert len(snap['findings'])==2
    assert all(len(f['evidence'])==2 for f in snap['findings'])


def test_zap_location_and_severity():
    data={'@version':'2.16.1','created':'2026-11-02T00:00:00Z','site':[{'@name':'http://127.0.0.1:8765/','alerts':[{'pluginid':'10021','riskcode':'1','confidence':'2','alert':'Example schema alert','desc':'Synthetic unit fixture only','instances':[{'uri':'http://127.0.0.1:8765/a','method':'GET','evidence':'fixture'}],'solution':'Review'}]}]}
    rows=parse('zap',json.dumps(data).encode())
    assert rows[1].severity=='low'
    assert rows[1].source_ref=='/site/0/alerts/0/instances/0'
    data['site'][0]['alerts'][0]['instances'][0]['uri']='http://127.0.0.2:8765/a'
    with pytest.raises(ValueError): parse('zap',json.dumps(data).encode())


def test_timeout_is_recorded_failure(store,scope,monkeypatch):
    import httpx
    a=store.create('timeout injection test',scope); c=store.add_check(a,action())
    def timeout(*args,**kwargs): raise httpx.ReadTimeout('Synthetic failure injection')
    monkeypatch.setattr(httpx.Client,'stream',timeout)
    execute(store,c,store.approve(c,'Test analyst'))
    snap=store.snapshot(a)
    assert snap['checks'][0]['state']==State.FAILED
    assert snap['checks'][0]['attempts'][0]['status']=='timeout'
    assert not snap['artifacts']


def test_import_denial_audit(store,scope):
    a=store.create('malformed import',scope)
    with pytest.raises(ValueError): store.ingest(a,'zap',b'null')
    assert store.snapshot(a)['events'][-1]['kind']=='import_denied'


def test_approval_invalidated_by_scope_change(store,scope):
    a=store.create('scope revision change',scope);c=store.add_check(a,action());approval=store.approve(c,'Analyst')
    with store.tx() as db: db.execute('UPDATE assessments SET scope=? WHERE id=?',(scope.model_copy(update={'revision':2}).model_dump_json(),a))
    with pytest.raises(ValueError): store.claim(c,approval)
    assert not store.snapshot(a)['checks'][0]['attempts']


def test_planning_explains_alternatives_and_drawbacks(store,scope):
    a=store.create('Assess web service',scope)
    proposal=plan(store,a)
    assert proposal.checks
    assert all(c.alternatives and c.drawback for c in proposal.checks)
    decision=next(e for e in store.snapshot(a)['events'] if e['kind']=='planning_decision')
    assert decision['payload']['checks'][0]['alternatives']
    with TestClient(create_app(store.path)) as client:
        page=client.get(f'/assessments/{a}').text
        assert 'Why not zap?' in page and 'Limit of this choice:' in page


def test_model_missing_tradeoffs_is_rejected(store,scope):
    a=store.create('Assess web service',scope)
    proposal=Proposal(mode='model',explanation='A proposed initial web check.',checks=[ProposedCheck(action=action(),rationale='Inspect the allowed response header.',evidence_ids=[])])
    with pytest.raises(ValueError,match='alternative'):
        validate_proposal(proposal,store.snapshot(a))
