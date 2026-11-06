import json
from fastapi.testclient import TestClient
from coverageproof.hosted import create_hosted_app


def test_hosted_authentication_and_fixed_fixture_scope(tmp_path, monkeypatch):
    monkeypatch.setenv('COVERAGEPROOF_DEMO_PASSWORD','synthetic-test-password-only')
    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME','demo.example.com')
    app = create_hosted_app(tmp_path/'demo.sqlite')
    client = TestClient(app, base_url='https://demo.example.com')
    assert client.get('/').url.path == '/login'
    assert 'Sign in to CoverageProof' in client.get('/').text
    assert client.get('/health').status_code == 200
    auth = ('demo','synthetic-test-password-only')
    assert client.get('/', auth=auth).status_code == 200
    scope = dict(name='Owned',networks=['127.0.0.2/32'],ports=[8765],authorization_reference='Synthetic owned fixture')
    response = client.post('/assessments',auth=auth,data={'request_text':'Hosted scope test','scope_json':json.dumps(scope)})
    assert response.status_code == 422
    scope['networks']=['127.0.0.1/32']
    assert client.post('/assessments',auth=auth,data={'request_text':'Hosted scope test','scope_json':json.dumps(scope)}).status_code == 200
    assert client.post('/assessments',auth=auth,headers={'Origin':'https://elsewhere.example'},data={}).status_code == 403


def test_browser_login_session_and_protected_data(tmp_path, monkeypatch):
    monkeypatch.setenv('COVERAGEPROOF_DEMO_PASSWORD', 'synthetic-test-password-only')
    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME', 'demo.example.com')
    client = TestClient(create_hosted_app(tmp_path/'demo.sqlite'), base_url='https://demo.example.com')
    assert client.get('/api/assessments/private').status_code == 401
    assert client.post('/login', data={'username': 'demo', 'password_input': 'wrong'}).status_code == 401
    assert not client.cookies
    data = {'username': 'demo', 'password_input': 'synthetic-test-password-only'}
    assert client.post('/login', data=data, headers={'Origin': 'https://elsewhere.example'}).status_code == 403
    response = client.post('/login', data=data, follow_redirects=False)
    assert response.status_code == 303
    cookie = response.headers['set-cookie']
    assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=strict' in cookie
    assert client.get('/', follow_redirects=False).status_code == 200
    assert client.get('/').headers['cache-control'] == 'no-store'
    token = client.cookies.get('__Host-coverageproof_session')
    client.cookies.set('__Host-coverageproof_session', token[:-1] + ('a' if token[-1] != 'a' else 'b'),
                       domain='demo.example.com', path='/')
    assert client.get('/', follow_redirects=False).status_code == 303
    client.cookies.clear()
    client.post('/login', data=data)
    client.post('/logout')
    assert client.get('/', follow_redirects=False).status_code == 303


def test_expired_session_cannot_access_workspace(tmp_path, monkeypatch):
    monkeypatch.setenv('COVERAGEPROOF_DEMO_PASSWORD', 'synthetic-test-password-only')
    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME', 'demo.example.com')
    client = TestClient(create_hosted_app(tmp_path/'demo.sqlite'), base_url='https://demo.example.com')
    client.post('/login', data={'username': 'demo', 'password_input': 'synthetic-test-password-only'})
    import time
    now = time.time()
    monkeypatch.setattr('coverageproof.hosted.time.time', lambda: now + 8 * 60 * 60 + 1)
    assert client.get('/', follow_redirects=False).status_code == 303
