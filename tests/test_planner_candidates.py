import pytest
from coverageproof.domain import Action, Receipt, State, now
from coverageproof.planner import eligible_followups, model_context, Proposal, validate_proposal


def setup(store, scope):
    a = store.create('Investigate missing response evidence', scope)
    root = store.add_check(a, Action(check='header-nosniff', target='http://127.0.0.1:8765/', scope_revision=1))
    admin = store.add_check(a, Action(check='header-nosniff', target='http://127.0.0.1:8765/admin', scope_revision=1))
    attempt, _, _ = store.claim(root, store.approve(root, 'Unit analyst'))
    store.finish(attempt, 'completed', 'Synthetic header observation', b'unit response', Receipt(
        target='http://127.0.0.1:8765/', check='header-nosniff', outcome=State.FINDING,
        issue_class='header:x-content-type-options', detail='Synthetic missing header', source_ref='unit', observed_at=now()))
    return a, root, admin


def proposal(action, evidence):
    return Proposal.model_validate({'mode':'model', 'explanation':'Investigate an unresolved response condition.', 'checks':[
        {'action':action, 'rationale':'Collect evidence for the selected response condition.', 'evidence_ids':evidence,
         'alternatives':[{'tool':'nikto','reason_not_chosen':'A broader scan is unnecessary for this exact response.'}],
         'drawback':'One response cannot establish every route or security condition.'}]})


def test_root_subtree_allows_admin_and_completed_root_is_not_candidate(store, scope):
    a, root, admin = setup(store, scope)
    snap = store.snapshot(a)
    candidates = model_context(snap)['eligible_followups']
    assert [c['check_id'] for c in candidates] == [admin]
    assert candidates[0]['policy_verdict'] == 'allowed'
    evidence = [snap['checks'][0]['observations'][0]['id']]
    validate_proposal(proposal(snap['checks'][1]['action'], evidence), snap)
    with pytest.raises(ValueError, match='eligible declared'):
        validate_proposal(proposal(snap['checks'][0]['action'], evidence), snap)


def test_exclusion_wins_over_root_subtree(store, scope):
    a, _, _ = setup(store, scope)
    snap = store.snapshot(a)
    snap['scope']['excluded_paths'] = ['/admin']
    assert eligible_followups(snap) == []


def test_multiple_unanswered_actions_remain_choices(store, scope):
    a, _, admin = setup(store, scope)
    other = store.add_check(a, Action(check='tcp-port', target='127.0.0.1', port=8766, scope_revision=1))
    candidates = eligible_followups(store.snapshot(a))
    assert {c['check_id'] for c in candidates} == {admin, other}
    assert next(c for c in candidates if c['check_id'] == other)['execution_mode'] == 'import_only'


def test_conflict_allows_a_targeted_repeat_and_no_action_is_valid(store, scope):
    a, root, _ = setup(store, scope)
    snap = store.snapshot(a)
    snap['findings'][0]['validation_status'] = 'conflicting_observations'
    assert root in {c['check_id'] for c in eligible_followups(snap)}
    validate_proposal(proposal(snap['checks'][0]['action'], [snap['checks'][0]['observations'][0]['id']]), snap)
    empty = Proposal(mode='model', explanation='Additional analyst information is needed before choosing a useful action.', checks=[])
    assert validate_proposal(empty, snap).checks == []


def test_proposals_are_available_before_execution_approval(store, scope):
    from coverageproof.planner import SYSTEM_PROMPT
    a = store.create('Inspect the admin response', scope)
    store.add_check(a, Action(check='header-nosniff', target='http://127.0.0.1:8765/admin', scope_revision=1))
    snap = store.snapshot(a)
    assert not snap['approvals']
    context = model_context(snap)
    candidate = context['eligible_followups'][0]
    assert candidate['proposal_allowed_now'] is True
    assert candidate['execution_approval_required_after_proposal'] is True
    assert 'proposal_only' in context['workflow_stage']
    assert 'may be proposed now without an existing execution approval' in SYSTEM_PROMPT
    validate_proposal(proposal(candidate['action'], []), snap)
    assert not store.snapshot(a)['approvals']


def test_followup_citations_required_without_transferring_findings(store, scope):
    from coverageproof.planner import model_plan_schema
    a, _, _ = setup(store, scope)
    snap = store.snapshot(a)
    context = model_context(snap)
    assert context['citation_policy']['required'] is True
    assert model_plan_schema(snap)['$defs']['ProposedCheck']['properties']['evidence_ids']['minItems'] == 1
    action = context['eligible_followups'][0]['action']
    with pytest.raises(ValueError, match='must cite stored observations'):
        validate_proposal(proposal(action, []), snap)
    with pytest.raises(ValueError, match='nonexistent observation'):
        validate_proposal(proposal(action, ['invented']), snap)
    evidence = [context['checks'][0]['observations'][0]['id']]
    validate_proposal(proposal(action, evidence), snap)
    assert snap['checks'][1]['observations'] == []


def test_initial_plan_schema_allows_no_citations(store, scope):
    from coverageproof.planner import model_plan_schema
    snap = store.snapshot(store.create('Initial assessment', scope))
    assert model_context(snap)['citation_policy']['required'] is False
    assert 'minItems' not in model_plan_schema(snap)['$defs']['ProposedCheck']['properties']['evidence_ids']
