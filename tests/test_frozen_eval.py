import json
import pytest
from coverageproof.store_eval import freeze, request_aware
from coverageproof.frozen_eval import run


def test_frozen_eval_hash_preflight_and_provider_stop(tmp_path):
    source=tmp_path/'source'
    frozen=freeze(source)
    class Limited:
        trace={'http_status':429}
        raw_output=b'rate limited'
        def propose(self,snapshot):raise ValueError('rate limited')
    with pytest.raises(ValueError,match='SHA256'):
        run(source/'cases.json','wrong',tmp_path/'bad',True,Limited)
    assert not (tmp_path/'bad').exists()
    result=run(source/'cases.json',frozen['suite_sha256'],tmp_path/'result',True,Limited)
    assert result['provider_calls']==1 and result['unattempted_cases']==5
    assert result['status']=='stopped_provider_failure'
    assert (tmp_path/'result'/'cases.json').read_bytes()==(source/'cases.json').read_bytes()
    assert (tmp_path/'result'/'01.output.txt').read_bytes()==b'rate limited'
    assert not result['rows'][0]['selection_pass']


def test_baseline_reads_request_and_dry_eval_never_constructs_provider(tmp_path):
    source=tmp_path/'source'
    frozen=freeze(source)
    def forbidden():raise AssertionError('provider constructed')
    result=run(source/'cases.json',frozen['suite_sha256'],tmp_path/'dry',False,forbidden)
    assert result['provider_calls']==0 and all(r['baseline_pass'] for r in result['rows'])
    case=json.loads((source/'cases.json').read_bytes())[0]
    case['snapshot']['request']='Do not propose any further checks.'
    assert request_aware(case['snapshot'])==[]
