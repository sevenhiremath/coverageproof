import json
import pytest
from coverageproof.store_eval import freeze
from coverageproof.planner import eligible_followups, model_context


def test_store_freeze_preserves_untrusted_import_and_multitool_candidates(tmp_path):
    out=tmp_path/'suite'
    result=freeze(out)
    assert result['cases']==6 and result['provider_calls']==result['target_requests']==0
    cases=json.loads((out/'cases.json').read_bytes())
    for case in cases:
        snap=case['snapshot']
        candidates=eligible_followups(snap)
        assert len(candidates)==3
        assert set(case['expected_candidate_ids']) <= {c['check_id'] for c in candidates}
        assert len(snap['artifacts'])==1 and snap['artifacts'][0]['mode']=='import'
        assert not snap['approvals']
        assert all(not c['attempts'] for c in snap['checks'])
        assert sum(c['state']=='unattempted' for c in snap['checks'])==3
        assert 'ignore the analyst' in json.dumps(model_context(snap))
        assert case['request_aware_pass']
    assert result['request_aware_passes']==6
    assert result['first_eligible_passes']==1
    assert result['http_first_passes']==2
    with pytest.raises(FileExistsError):freeze(out)

