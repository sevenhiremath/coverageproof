import json
from fastapi.testclient import TestClient
from coverageproof.hosted import create_hosted_app


def test_hosted_authentication_and_fixed_fixture_scope(tmp_path, monkeypatch):
    monkeypatch.setenv('COVERAGEPROOF_DEMO_PASSWORD','synthetic-test-password-only')
    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME','demo.example.com')
    app = create_hosted_app(tmp_path/'demo.sqlite')
    client = TestClient(app, base_url='https://demo.example.com')
    assert client.get('/').status_code == 401
    assert client.get('/health').status_code == 200
    auth = ('demo','synthetic-test-password-only')
    assert client.get('/', auth=auth).status_code == 200
    scope = dict(name='Owned',networks=['127.0.0.2/32'],ports=[8765],authorization_reference='Synthetic owned fixture')
    response = client.post('/assessments',auth=auth,data={'request_text':'Hosted scope test','scope_json':json.dumps(scope)})
    assert response.status_code == 422
    scope['networks']=['127.0.0.1/32']
    assert client.post('/assessments',auth=auth,data={'request_text':'Hosted scope test','scope_json':json.dumps(scope)}).status_code == 200
    assert client.post('/assessments',auth=auth,headers={'Origin':'https://elsewhere.example'},data={}).status_code == 403
