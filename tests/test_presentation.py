from coverageproof.presentation import action_facts, applicability_note


def test_scope_and_operation_facts_are_independent_of_model_reasoning():
    scope=dict(name='Owned',networks=['127.0.0.1/32'],ports=[8765],authorization_reference='Owned fixture')
    action=dict(check='header-nosniff',target='http://127.0.0.1:8765/admin',scope_revision=1)
    assert 'Allowed' in action_facts(action,scope)['scope']
    assert 'one HTTP GET' in action_facts(action,scope)['operation']
    action['check']='web-alerts'
    assert 'imported' in action_facts(action,scope)['operation']
    assert 'Missing findings' in action_facts(action,scope)['limit']
    scope['excluded_paths']=['/admin']
    assert 'failed' in action_facts(action,scope)['scope']


def test_hsts_warning_requires_plain_http_and_matching_source_claim():
    finding=dict(asset='http://127.0.0.1:8765/',source_observations=[dict(detail='Missing strict-transport-security')])
    assert 'HTTPS endpoint' in applicability_note(finding)
    finding['asset']='https://127.0.0.1:8765/'
    assert applicability_note(finding) is None
