import pytest
from coverageproof.planner_eval import cases, run
from coverageproof.planner import eligible_followups


def test_expected_actions_are_eligible_and_cases_are_independent():
    suite=cases()
    assert len({c['id'] for c in suite}) == 12
    for case in suite:
        eligible={c['action']['target'].rsplit('/',1)[-1] for c in eligible_followups(case['snapshot'])}
        assert set(case['expected']) <= eligible
    assert suite[0]['snapshot']['scope']['excluded_paths'] == []


def test_dry_run_never_calls_provider_and_refuses_overwrite(tmp_path,monkeypatch):
    def forbidden(*args):
        raise AssertionError('Dry evaluation must not contact a provider')
    monkeypatch.setattr('coverageproof.planner_eval.GroqProvider.propose',forbidden)
    out=tmp_path/'evaluation'
    result=run(out)
    assert len(result['rows']) == 12
    assert sum(r['baseline_pass'] for r in result['rows']) == 10
    assert all('proposal' not in row for row in result['rows'])
    with pytest.raises(FileExistsError):
        run(out)


def test_live_http_failure_stops_without_retry(tmp_path, monkeypatch):
    import json
    calls=[]
    class FailingProvider:
        def propose(self, snapshot):
            calls.append(snapshot)
            self.trace={'http_status':429}
            self.raw_output=b''
            raise ValueError('Provider failed')
    monkeypatch.setattr('coverageproof.planner_eval.GroqProvider',FailingProvider)
    result=run(tmp_path/'live',live=True)
    assert len(calls)==1
    assert len(result['rows'])==1
    assert result['rows'][0]['selection_pass'] is False
    saved=json.loads((tmp_path/'live'/'results.json').read_text())
    assert saved==result


def test_invalid_model_proposals_are_failures_not_retried(tmp_path, monkeypatch):
    calls=[]
    class InvalidProvider:
        def propose(self, snapshot):
            calls.append(snapshot)
            self.trace={'http_status':200}
            self.raw_output=b'{"invalid":"synthetic test"}'
            raise ValueError('Invalid proposal')
    monkeypatch.setattr('coverageproof.planner_eval.GroqProvider',InvalidProvider)
    result=run(tmp_path/'live',live=True)
    assert len(calls)==12
    assert all(not row['valid'] and not row['selection_pass'] for row in result['rows'])
    assert len(list((tmp_path/'live').glob('*.output.txt')))==12
