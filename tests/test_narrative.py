"""Model prose here is a mocked unit fixture, never live inference."""
import json
from io import BytesIO
import pytest
from pypdf import PdfReader
from coverageproof.domain import Action, Receipt, State, now
from coverageproof.narrative import draft_report, review_draft
from coverageproof.report import generate


class FakeProvider:
    def __init__(self,check,evidence):self.check,self.evidence=check,evidence
    def structured(self,schema,prompt,context):
        item={'text':'Only the declared response-header condition was observed in this unit fixture.','check_ids':[self.check],'evidence_ids':self.evidence}
        return json.dumps({'mode':'model','executive_summary':[item],'limitations':[dict(item,text='Other routes and vulnerability classes remain outside the recorded check.')]})


def setup(store,scope):
    a=store.create('Review report explanations',scope)
    c=store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/',scope_revision=1))
    attempt,_,_=store.claim(c,store.approve(c,'Unit analyst'))
    r=Receipt(target='http://127.0.0.1:8765/',check='header-nosniff',outcome=State.NOT_OBSERVED,detail='Unit fixture response has nosniff',source_ref='Synthetic unit receipt',observed_at=now())
    store.finish(attempt,'completed','Synthetic unit result',b'Unit fixture, not genuine scanner output',r)
    obs=store.snapshot(a)['checks'][0]['observations'][0]['id']
    return a,c,obs


def pdf_text(store,a):return ' '.join(' '.join(p.extract_text() for p in PdfReader(BytesIO(generate(store,a))).pages).split())


def test_draft_requires_real_related_citations(store,scope):
    a,c,obs=setup(store,scope)
    with pytest.raises(ValueError,match='valid observation'):
        draft_report(store,a,FakeProvider(c,['missing-observation']))
    with pytest.raises(ValueError,match='must cite their observations'):
        draft_report(store,a,FakeProvider(c,[]))
    other=store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1))
    with pytest.raises(ValueError,match='does not belong'):
        draft_report(store,a,FakeProvider(other,[obs]))
    assert not store.snapshot(a)['report_draft']
    assert len([e for e in store.snapshot(a)['events'] if e['kind']=='report_draft_failed'])==3


def test_unapproved_or_changed_draft_cannot_enter_pdf(store,scope):
    a,c,obs=setup(store,scope)
    draft_report(store,a,FakeProvider(c,[obs]))
    snap=store.snapshot(a);d=snap['report_draft'];event=d['event']
    phrase='Other routes and vulnerability classes remain outside the recorded check.'
    assert d['current'] and d['review'] is None
    assert phrase not in pdf_text(store,a)
    review_draft(store,a,event['id'],event['payload']['basis'],'Unit analyst','Reviewed each cited statement and the stated limitations')
    assert phrase in pdf_text(store,a)
    store.add_check(a,Action(check='tcp-port',target='127.0.0.1',port=8766,scope_revision=1))
    other=store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1))
    with pytest.raises(ValueError,match='does not belong'):
        draft_report(store,a,FakeProvider(other,[obs]))
    assert not store.snapshot(a)['report_draft']['current']
    assert phrase not in pdf_text(store,a)
    with pytest.raises(ValueError,match='changed'):
        review_draft(store,a,event['id'],event['payload']['basis'],'Unit analyst','Cannot accept the earlier draft after plan changes')


def test_development_mode_never_masquerades_as_report_ai(store,scope,monkeypatch):
    a,c,obs=setup(store,scope)
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','development')
    with pytest.raises(ValueError,match='No development prose'):
        draft_report(store,a)
