"""Scope/freshness tests use controlled timestamps and synthetic native fixtures."""
from datetime import datetime, timezone
import pytest
from coverageproof.domain import Action, Scope, State, canonical_target, validate_scope, now
from coverageproof.freshness import freshness, collection_time


def web(path):return Action(check='header-nosniff',target='http://127.0.0.1:8765'+path,scope_revision=1)


def test_path_boundaries_are_segment_based(scope):
    scoped=scope.model_copy(update={'allowed_paths':('/app',),'excluded_paths':('/app/admin',)})
    for path in ['/app','/app/','/app/public','/app/administer']:
        validate_scope(scoped,web(path))
    for path in ['/application','/other','/app/admin','/app/admin/child','/app/admin?x=y']:
        with pytest.raises(ValueError):validate_scope(scoped,web(path))


@pytest.mark.parametrize('path',['//admin','/./admin','/app//admin','/admin;ignored','/%61dmin','/app/../admin'])
def test_ambiguous_paths_cannot_bypass_exclusions(path):
    with pytest.raises(ValueError):canonical_target('http://127.0.0.1:8765'+path)


@pytest.mark.parametrize('paths',[(),('/app/../admin',),('/./admin',),('//admin',),('/admin?x',)])
def test_invalid_scope_path_settings_rejected(paths):
    with pytest.raises(ValueError):Scope(name='scope',networks=('127.0.0.1/32',),ports=(8765,),allowed_paths=paths,authorization_reference='Owned unit fixture')


def test_native_collection_formats_and_age():
    ref=datetime(2026,11,2,12,tzinfo=timezone.utc)
    for value in ['2026-11-02T11:00:00Z','2026-11-02 11:00:00 +0000','Mon, 02 Nov 2026 11:00:00 GMT',str(int(datetime(2026,11,2,11,tzinfo=timezone.utc).timestamp()))]:
        assert freshness(value,24,reference=ref)['state']=='current_window'
    assert freshness('2026-10-01T11:00:00Z',24,reference=ref)['state']=='stale'
    assert freshness('2026-11-03T11:00:00Z',24,reference=ref)['state']=='future_timestamp'
    for value in [None,'missing','2026-11-02T11:00:00','999999999999999999999999999999999999']:
        assert freshness(value,24,reference=ref)['state']=='unknown'


def xml(collected):
    end='' if collected is None else f'endtime="{collected}"'
    return f'<nmaprun scanner="nmap" xmloutputversion="1.05"><host {end}><status state="up"/><address addr="127.0.0.1" addrtype="ipv4"/><ports><port protocol="tcp" portid="8765"><state state="closed" reason="reset"/></port></ports></host><runstats><finished exit="success"/></runstats></nmaprun>'.encode()


def test_old_import_is_stale_even_when_imported_now(store,scope):
    a=store.create('Old source evidence',scope)
    store.add_check(a,Action(check='tcp-port',target='127.0.0.1',port=8765,scope_revision=1))
    store.ingest(a,'nmap',xml('1000'))
    snap=store.snapshot(a)
    assert snap['checks'][0]['state']==State.STALE
    o=snap['checks'][0]['observations'][0]
    assert o['receipt']['outcome']==State.NOT_OBSERVED
    assert o['freshness']['state']=='stale'
    assert snap['artifacts'][0]['created']!='1000'


def test_unknown_time_cannot_create_current_negative(store,scope):
    a=store.create('Unknown source time',scope)
    store.add_check(a,Action(check='tcp-port',target='127.0.0.1',port=8765,scope_revision=1))
    store.ingest(a,'nmap',xml(None))
    snap=store.snapshot(a)
    assert snap['checks'][0]['state']==State.INCONCLUSIVE
    assert snap['checks'][0]['observations'][0]['freshness']['state']=='unknown'


def test_scope_change_execution_denial_is_audited(store,scope):
    a=store.create('Changed scope',scope);c=store.add_check(a,web('/'))
    approval=store.approve(c,'Analyst')
    with store.tx() as db:db.execute('UPDATE assessments SET scope=? WHERE id=?',(scope.model_copy(update={'revision':2}).model_dump_json(),a))
    with pytest.raises(ValueError):store.claim(c,approval)
    denied=[e for e in store.snapshot(a)['events'] if e['kind']=='execution_denied']
    assert len(denied)==1 and 'revision' in denied[0]['payload']['reason']
