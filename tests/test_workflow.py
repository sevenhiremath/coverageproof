"""Workflow tests. Scanner/model responses here are synthetic test data, not demos."""
from io import BytesIO
import json
import httpx
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from coverageproof.app import create_app
from coverageproof.domain import Action, Receipt, State, now
from coverageproof.planner import plan, model_context
from coverageproof.report import generate


def native_nikto():
    return json.dumps([{'host':'127.0.0.1','ip':'127.0.0.1','port':'8765','start_time':'unit fixture','end_time':'unit fixture','vulnerabilities':[{'id':'test-1','url':'/admin','msg':'Synthetic issue for review tests','method':'GET'}]}]).encode()


def assessed(store,scope):
    a=store.create('Review a web-server observation',scope)
    store.add_check(a,Action(check='web-server',target='http://127.0.0.1:8765/admin',scope_revision=1))
    store.ingest(a,'nikto',native_nikto())
    return a,store.snapshot(a)['findings'][0]


def test_review_persists_and_new_evidence_invalidates(store,scope):
    a,f=assessed(store,scope)
    store.review_finding(a,f['id'],'accepted_for_report','Reviewed source and scope; needs no broader claim.','Swayam',f['evidence_digest'])
    snap=store.snapshot(a)
    assert snap['findings'][0]['status']=='accepted_for_report'
    # Duplicate import is another evidence record; reviewer must see it, no evidence is lost.
    store.ingest(a,'nikto',native_nikto())
    snap=store.snapshot(a)
    assert snap['findings'][0]['status']=='review_outdated'
    assert len(snap['findings'][0]['evidence'])==2
    with pytest.raises(ValueError,match='Evidence changed'):
        store.review_finding(a,f['id'],'false_positive','Outdated review should be rejected.','Swayam',f['evidence_digest'])


def test_false_positive_and_report_share_review_state(store,scope):
    a,f=assessed(store,scope)
    store.review_finding(a,f['id'],'false_positive','Manual investigation found this test issue inapplicable.','Analyst',f['evidence_digest'])
    snap=store.snapshot(a)
    assert snap['findings'][0]['evidence']
    assert snap['findings'][0]['review']['note'].startswith('Manual investigation')
    text='\n'.join(p.extract_text() for p in PdfReader(BytesIO(generate(store,a))).pages)
    assert 'false_positive' in text and 'Manual investigation' in text
    assert 'Imported observations not yet in the declared plan' in text
    with store.tx() as db:
        stored=json.loads(db.execute('SELECT snapshot FROM reports WHERE assessment=? ORDER BY rowid DESC LIMIT 1',(a,)).fetchone()['snapshot'])
    assert stored['findings'][0]['status']=='false_positive'


def test_review_cannot_target_another_assessment(store,scope):
    a,f=assessed(store,scope);other=store.create('Separate assessment',scope)
    with pytest.raises(KeyError):
        store.review_finding(other,f['id'],'accepted_for_report','Trying another assessment must fail.','Analyst',f['evidence_digest'])
    for decision,note in [('confirmed_secure','This status is unsupported'),('false_positive','short')]:
        with pytest.raises(ValueError):store.review_finding(a,f['id'],decision,note,'Analyst',f['evidence_digest'])


def test_unmatched_import_retained_and_adopted_once(store,scope):
    a=store.create('Import before planning',scope)
    artifact=store.ingest(a,'nikto',native_nikto())
    snap=store.snapshot(a)
    assert not snap['checks'] and not snap['findings']
    assert len(snap['unmatched'])==2
    o=next(x for x in snap['unmatched'] if x['receipt']['issue_class'])
    check=store.adopt_observation(a,o['id'])
    assert store.adopt_observation(a,o['id'])==check
    snap=store.snapshot(a)
    assert len(snap['checks'])==1 and len(snap['findings'])==1
    assert snap['findings'][0]['evidence'][0]['artifact']==artifact
    assert snap['findings'][0]['evidence'][0]['observation']==o['id']
    assert len(snap['unmatched'])==1
    with pytest.raises(KeyError):store.adopt_observation(store.create('Other',scope),o['id'])


def test_review_and_adopt_routes(store,scope):
    a,f=assessed(store,scope)
    with TestClient(create_app(store.path)) as client:
        r=client.post(f'/assessments/{a}/findings/{f["id"]}/review',data={'disposition':'needs_review','note':'Need one more source observation.','actor':'Analyst','evidence_digest':f['evidence_digest']})
        assert r.status_code==200 and 'Need one more source observation.' in r.text
        o=store.snapshot(a)['unmatched'][0]
        r=client.post(f'/assessments/{a}/observations/{o["id"]}/adopt')
        assert r.status_code==200 and 'No unassigned imported observations.' in r.text


def proposal_json():
    return {'mode':'model','explanation':'The requested endpoint still needs its response header checked.','checks':[{'action':{'check':'header-nosniff','target':'http://127.0.0.1:8765/admin','scope_revision':1},'rationale':'Check the exact endpoint requested by the analyst.','evidence_ids':[],'alternatives':[{'tool':'nikto','reason_not_chosen':'A broader server scan does not answer this single response question as directly.'}],'drawback':'One response cannot establish the behavior of every endpoint.'}]}


def mock_ollama(monkeypatch,result,status=200):
    actual=httpx.Client
    captured=[]
    def respond(request):
        captured.append(request)
        return httpx.Response(status,json=result)
    def factory(**kwargs):
        return actual(transport=httpx.MockTransport(respond),**kwargs)
    monkeypatch.setattr(httpx,'Client',factory)
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','ollama')
    return captured


def test_local_model_contract_adds_plan_but_never_executes(store,scope,monkeypatch):
    a=store.create('Check admin response headers',scope)
    requests=mock_ollama(monkeypatch,{'done':True,'done_reason':'stop','message':{'content':json.dumps(proposal_json())}})
    proposal=plan(store,a)
    assert proposal.mode=='model'
    snap=store.snapshot(a)
    assert snap['checks'][0]['state']==State.UNATTEMPTED
    assert not snap['approvals'] and not snap['artifacts']
    assert str(requests[0].url)=='http://127.0.0.1:11434/api/chat'
    payload=json.loads(requests[0].content)
    assert payload['stream'] is False and payload['format']['type']=='object'
    assert payload['keep_alive']==0
    assert next(e for e in snap['events'] if e['kind']=='planning_decision')['payload']['provider']=='ollama'


@pytest.mark.parametrize('result,status',[
    ({'done':False,'message':{'content':'{}'}},200),
    ({'done':True,'done_reason':'length','message':{'content':'{}'}},200),
    ({'done':True,'message':{'content':'not json'}},200),
    ({'done':True},200),
    ({'error':'missing model'},404),
])
def test_local_model_failure_adds_no_plan(store,scope,monkeypatch,result,status):
    a=store.create('Invalid local model test',scope)
    mock_ollama(monkeypatch,result,status)
    with pytest.raises(ValueError):plan(store,a)
    snap=store.snapshot(a)
    assert not snap['checks']
    assert snap['events'][-1]['kind']=='planning_failed'


def test_local_model_nonexistent_evidence_rejected(store,scope,monkeypatch):
    a=store.create('Citation validation',scope);p=proposal_json();p['checks'][0]['evidence_ids']=['invented-id']
    mock_ollama(monkeypatch,{'done':True,'message':{'content':json.dumps(p)}})
    with pytest.raises(ValueError,match='nonexistent'):plan(store,a)
    assert not store.snapshot(a)['checks']


def test_completed_development_plan_is_not_proposed_again(store,scope,monkeypatch):
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','development')
    a=store.create('Check response',scope)
    c=store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/',scope_revision=1))
    attempt,_,_=store.claim(c,store.approve(c,'Analyst'))
    store.finish(attempt,'completed','Synthetic test receipt',b'test',Receipt(target='http://127.0.0.1:8765/',check='header-nosniff',outcome=State.NOT_OBSERVED,detail='Synthetic development fixture only',source_ref='test',observed_at=now()))
    assert plan(store,a).checks==[]
