import pytest
from coverageproof.domain import Action, Scope
from coverageproof.store import Store


def test_applicability_is_attributed_and_invalidated_by_execution(tmp_path):
    s=Store(tmp_path/'a.db')
    a=s.create('Check the owned fixture',Scope(name='owned',networks=('127.0.0.1/32',),ports=(8765,),authorization_reference='Self-owned fixture authorization'))
    c=s.add_check(a,Action(check='header-nosniff',target='http://127.0.0.1:8765/',scope_revision=1))
    s.set_applicability(c,'not_applicable','Owner excludes response-header analysis from this methodology','Analyst')
    snap=s.snapshot(a)
    assert snap['checks'][0]['state']=='not_applicable'
    assert snap['checks'][0]['applicability']['current']
    with pytest.raises(ValueError,match='not applicable'):
        s.claim(c,s.approve(c,'Analyst'))
    s.set_applicability(c,'applicable','Owner now includes response-header analysis','Analyst')
    attempt,_,_=s.claim(c,s.approve(c,'Analyst'))
    s.finish(attempt,'timeout','Synthetic timeout injection')
    snap=s.snapshot(a)
    assert snap['checks'][0]['state']=='failed'
    assert not snap['checks'][0]['applicability']['current']
    with pytest.raises(ValueError,match='cannot replace'):
        s.set_applicability(c,'not_applicable','A timeout is not an applicability reason','Analyst')
