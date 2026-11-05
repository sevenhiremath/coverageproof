"""Password-protected hosted demo with a fixed, owned loopback fixture."""
import base64
from contextlib import asynccontextmanager
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from threading import Thread

from fastapi.responses import Response
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
        header = request.headers.get('authorization', '')
        valid = False
        if header.startswith('Basic '):
            try:
                credentials = base64.b64decode(header[6:], validate=True).decode('utf-8')
                valid = hmac.compare_digest(credentials.encode(), ('demo:' + password).encode())
            except (ValueError, UnicodeDecodeError):
                pass
        if not valid:
            return Response('Sign in to the CoverageProof demo', status_code=401,
                            headers={'WWW-Authenticate': 'Basic realm="CoverageProof demo"'})
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response

    return app
