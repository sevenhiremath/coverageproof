import json
import httpx
import pytest
from coverageproof.planner import plan
from coverageproof.groq_provider import GroqProvider


def mock(monkeypatch, response):
    actual=httpx.Client
    requests=[]
    def respond(request):
        requests.append(request)
        return response
    monkeypatch.setattr(httpx,'Client',lambda **kw:actual(transport=httpx.MockTransport(respond),**kw))
    monkeypatch.setenv('GROQ_API_KEY','unit-secret-key')
    monkeypatch.setenv('COVERAGEPROOF_PROVIDER','groq')
    return requests


def test_groq_records_real_provider_label_without_executing(store,scope,monkeypatch):
    reply=json.dumps({'mode':'model','explanation':'No useful action is selected in this synthetic provider test.','checks':[]})
    requests=mock(monkeypatch,httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':reply}}]}))
    a=store.create('Unit provider contract',scope)
    assert plan(store,a).mode=='model'
    assert str(requests[0].url)=='https://api.groq.com/openai/v1/chat/completions'
    assert json.loads(requests[0].content)['response_format']['type']=='json_schema'
    snap=store.snapshot(a)
    assert not snap['approvals'] and not snap['artifacts']
    assert 'unit-secret-key' not in json.dumps(snap)
    with store.tx() as db:
        row=db.execute('SELECT * FROM model_calls').fetchone()
        assert json.loads(row['metadata'])['provider']=='groq'
        assert row['raw_output']==reply.encode()


@pytest.mark.parametrize('status',[401,429,500,302])
def test_provider_errors_are_redacted_and_not_retried(monkeypatch,status):
    requests=mock(monkeypatch,httpx.Response(status,text='unit-private-error-body'))
    provider=GroqProvider()
    with pytest.raises(ValueError,match=f'HTTP {status}') as error:
        provider.structured({},'unit',{})
    assert 'unit-private' not in str(error.value)
    assert len(requests)==1 and provider.raw_output==b''
    assert provider.trace['elapsed_ms']>=0


def test_incomplete_response_is_not_accepted(monkeypatch):
    mock(monkeypatch,httpx.Response(200,json={'choices':[{'finish_reason':'length','message':{'content':'{"partial":true}'}}]}))
    provider=GroqProvider()
    with pytest.raises(ValueError,match='incomplete'):provider.structured({},'unit',{})
    assert provider.raw_output and not provider.trace['output_complete']


def test_missing_key_makes_no_call(monkeypatch):
    monkeypatch.delenv('GROQ_API_KEY',raising=False)
    with pytest.raises(ValueError,match='not configured'):GroqProvider().structured({},'unit',{})


def test_oversized_reply_is_not_saved(monkeypatch):
    mock(monkeypatch,httpx.Response(200,content=b'x'*262145))
    p=GroqProvider()
    with pytest.raises(ValueError,match='256 KiB'):p.structured({},'unit',{})
    assert p.raw_output==b''
