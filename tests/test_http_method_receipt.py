import httpx
from contextlib import contextmanager
from coverageproof.domain import Action
from coverageproof.runner import execute


def test_live_receipt_records_actual_get_method(store,scope,monkeypatch):
    assessment=store.create('Synthetic HTTP receipt verification',scope)
    check=store.add_check(assessment,Action(check='header-nosniff',target='http://127.0.0.1:8765/',scope_revision=1))
    class Client:
        def __init__(self,**kwargs):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        @contextmanager
        def stream(self,method,target,**kwargs):
            assert method=='GET'
            yield httpx.Response(200,stream=httpx.ByteStream(b'synthetic'),request=httpx.Request(method,target))
    monkeypatch.setattr('coverageproof.runner.httpx.Client',Client)
    execute(store,check,store.approve(check,'Unit analyst'))
    receipt=store.snapshot(assessment)['checks'][0]['observations'][0]['receipt']
    assert receipt['http_method']=='GET'
    assert receipt['outcome']=='finding_supported'
