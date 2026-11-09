"""Password-protected hosted demo with a fixed, owned loopback fixture."""
import base64
from contextlib import asynccontextmanager
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import secrets
from threading import Thread
import time

from fastapi import Form, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from .app import create_app


class DemoFixture(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in {'/', '/admin'}:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        if self.path == '/admin':
            self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(b'<html><title>CoverageProof owned demo</title><body>Owned fixture response.</body></html>')

    def log_message(self, *_):
        pass


def create_hosted_app(db_path=None):
    password = os.environ.get('COVERAGEPROOF_DEMO_PASSWORD', '')
    hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
    if len(password) < 20 or not hostname:
        raise ValueError('Hosted demo requires a password of at least 20 characters and an external hostname')
    app = create_app(db_path, hosted_hostname=hostname)
    templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))
    cookie_name = '__Host-coverageproof_session'
    session_seconds = 8 * 60 * 60

    def signature(payload):
        return hmac.new(password.encode(), ('session:' + payload).encode(), 'sha256').hexdigest()

    def valid_session(token):
        try:
            expires, nonce, supplied = token.split('.')
            remaining = int(expires) - time.time()
            return (0 < remaining <= session_seconds and bool(nonce)
                    and hmac.compare_digest(supplied, signature(expires + '.' + nonce)))
        except (ValueError, TypeError):
            return False

    @app.get('/login')
    def login_page(request: Request):
        return templates.TemplateResponse(request=request, name='login.html', context={'error': False})

    @app.post('/login')
    def login(request: Request, username: str = Form(), password_input: str = Form()):
        if not (hmac.compare_digest(username.encode(), b'demo')
                and hmac.compare_digest(password_input.encode(), password.encode())):
            return templates.TemplateResponse(request=request, name='login.html',
                                              context={'error': True}, status_code=401)
        payload = str(int(time.time()) + session_seconds) + '.' + secrets.token_urlsafe(24)
        response = RedirectResponse('/', status_code=303)
        response.set_cookie(cookie_name, payload + '.' + signature(payload), max_age=session_seconds,
                            secure=True, httponly=True, samesite='strict', path='/')
        return response

    @app.post('/logout')
    def logout():
        response = RedirectResponse('/login', status_code=303)
        response.delete_cookie(cookie_name, secure=True, httponly=True, samesite='strict', path='/')
        return response

    @asynccontextmanager
    async def lifespan(app):
        fixture = ThreadingHTTPServer(('127.0.0.1', 8765), DemoFixture)
        thread = Thread(target=fixture.serve_forever, daemon=True)
        thread.start()
        try:
            yield
        finally:
            fixture.shutdown()
            fixture.server_close()
            thread.join(timeout=5)

    app.router.lifespan_context = lifespan

    @app.middleware('http')
    async def authenticate(request, call_next):
        if request.url.path == '/health' and request.method == 'GET':
            return await call_next(request)
        if request.url.path == '/login':
            response = await call_next(request)
            response.headers['Cache-Control'] = 'no-store'
            return response
        header = request.headers.get('authorization', '')
        valid = valid_session(request.cookies.get(cookie_name, ''))
        if header.startswith('Basic '):
            try:
                credentials = base64.b64decode(header[6:], validate=True).decode('utf-8')
                valid = hmac.compare_digest(credentials.encode(), ('demo:' + password).encode())
            except (ValueError, UnicodeDecodeError):
                pass
        if not valid:
            if request.method == 'GET' and (request.url.path == '/' or 'text/html' in request.headers.get('accept', '')):
                return RedirectResponse('/login', status_code=303, headers={'Cache-Control': 'no-store'})
            return Response('Sign in to the CoverageProof demo', status_code=401,
                            headers={'WWW-Authenticate': 'Basic realm="CoverageProof demo"'})
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response

    return app
