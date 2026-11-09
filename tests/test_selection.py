import pytest
from coverageproof.domain import Action
from coverageproof.selection import Decision, resolve
from coverageproof.planner import validate_proposal, plan


def fixture(store,scope):
    a=store.create('Inspect the declared settings question',scope)
    c=store.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/settings',scope_revision=1))
    return a,c,store.snapshot(a)


def decision(c, **updates):
    item=dict(candidate_id=c,rationale='The declared question has no current answer.',
        basis=[dict(kind='check',id=c)],
        alternatives=[dict(kind='abstain',candidate_id=None,reason='Abstaining leaves this declared question unanswered.')],
        drawback='One response at one time cannot assess every route.')
    item.update(updates)
    return Decision(mode='model',explanation='Investigate the unanswered declared question.',selections=[item])


def test_resolves_exact_action_without_fabricated_observation(store,scope):
    a,c,s=fixture(store,scope)
    p=resolve(decision(c),s)
    validate_proposal(p,s)
    assert p.contract_version=='candidate-v2'
    assert p.checks[0].action.model_dump()==s['checks'][0]['action']
    assert p.checks[0].evidence_ids==[]
    assert not store.snapshot(a)['approvals']


def test_unknown_duplicate_and_unrelated_basis_rejected(store,scope):
    _,c,s=fixture(store,scope)
    with pytest.raises(ValueError,match='Unknown'):resolve(decision('invented'),s)
    d=decision(c);d.selections.append(d.selections[0])
    with pytest.raises(ValueError,match='duplicate'):resolve(d,s)
    with pytest.raises(ValueError,match='Basis'):resolve(decision(c,basis=[dict(kind='observation',id='invented')]),s)


def test_scope_change_invalidates_resolved_selection(store,scope):
    _,c,s=fixture(store,scope)
    p=resolve(decision(c),s)
    s['scope']['revision']=2
    with pytest.raises(ValueError):validate_proposal(p,s)


def test_empty_eligibility_has_backend_provenance_and_no_call(store,scope,monkeypatch):
    a,c,s=fixture(store,scope)
    with store.tx() as db:
        # Scope exclusion makes declared work ineligible.
        import json
        current=scope.model_copy(update={'excluded_paths':('/settings',)})
        db.execute('UPDATE assessments SET scope=? WHERE id=?',(current.model_dump_json(),a))
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','groq')
    monkeypatch.setattr('coverageproof.groq_provider.GroqProvider.propose',
        lambda *args:pytest.fail('No eligible work must not contact provider'))
    p=plan(store,a)
    assert p.mode=='backend' and p.checks==[]


def test_groq_followup_uses_selection_schema_and_saves_version(store,scope,monkeypatch):
    import json
    from test_groq import mock
    import httpx
    a,c,s=fixture(store,scope)
    reply=decision(c).model_dump_json()
    requests=mock(monkeypatch,httpx.Response(200,json={
        'choices':[{'finish_reason':'stop','message':{'content':reply}}]}))
    p=plan(store,a)
    assert p.contract_version=='candidate-v2'
    schema=json.loads(requests[0].content)['response_format']['json_schema']['schema']
    assert 'selections' in schema['properties'] and 'checks' not in schema['properties']
    snap=store.snapshot(a)
    assert len(snap['checks'])==1
    assert not snap['approvals'] and not snap['artifacts']
