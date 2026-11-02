import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from .domain import Action, Scope
from .store import Store
from .planner import plan
from .runner import execute
from .report import generate
from .narrative import draft_report, review_draft


def create_app(db_path=None):
    app = FastAPI(title='CoverageProof')
    store = Store(db_path or os.environ.get('COVERAGEPROOF_DB','data/coverageproof.sqlite'))
    app.state.store = store
    templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))

    @app.middleware('http')
    async def local_boundary(request, call_next):
        # Loopback product only. Host allowlist prevents DNS-rebinding access to local service.
        host = request.headers.get('host','').split(':')[0]
        if host not in {'127.0.0.1','localhost','testserver'}:
            return Response('Local single-analyst service only', status_code=403)
        if request.method == 'POST':
            origin = request.headers.get('origin')
            if origin and origin != f'{request.url.scheme}://{request.headers.get("host")}':
                return Response('Cross-origin mutation blocked',status_code=403)
            if request.headers.get('sec-fetch-site') == 'cross-site':
                return Response('Cross-site mutation blocked',status_code=403)
        result = await call_next(request)
        result.headers['X-Content-Type-Options'] = 'nosniff'
        result.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"
        return result

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return templates.TemplateResponse(request=request,name='error.html',context={'error':str(exc)},status_code=422)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return Response('Resource not found',status_code=404)

    @app.get('/health')
    def health():
        return {'status':'ok','scanner_execution':'disabled','provider':os.environ.get('COVERAGEPROOF_PROVIDER','development')}

    @app.get('/',response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse(request=request,name='index.html',context={'assessments':store.list_assessments()})

    @app.post('/assessments')
    def create(request_text: str=Form(),scope_json: str=Form()):
        scope = Scope.model_validate_json(scope_json)
        id = store.create(request_text,scope)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.get('/assessments/{id}',response_class=HTMLResponse)
    def assessment(request: Request,id: str):
        return templates.TemplateResponse(request=request,name='assessment.html',context={'a':store.snapshot(id)})

    @app.get('/api/assessments/{id}')
    def api(id: str):
        return store.snapshot(id)

    @app.post('/assessments/{id}/plan')
    def propose(id: str):
        plan(store,id)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/checks')
    def check(id: str, action_json: str=Form()):
        store.add_check(id,Action.model_validate_json(action_json))
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/checks/{id}/applicability')
    def applicability(id: str, decision: str=Form(), note: str=Form(), actor: str=Form()):
        store.set_applicability(id,decision,note,actor)
        with store.tx() as db:
            c,_,_ = store.check_context(db,id)
        return RedirectResponse(f'/assessments/{c["assessment"]}',303)

    @app.post('/checks/{id}/approve')
    def approve(request: Request,id: str,actor: str=Form()):
        store.approve(id,actor)
        with store.tx() as db:
            c,_,_ = store.check_context(db,id)
        return RedirectResponse(f'/assessments/{c["assessment"]}',303)

    @app.post('/checks/{id}/execute')
    def run(id: str, approval: str=Form()):
        execute(store,id,approval)
        with store.tx() as db:
            c,_,_ = store.check_context(db,id)
        return RedirectResponse(f'/assessments/{c["assessment"]}',303)

    @app.post('/assessments/{id}/imports')
    async def ingest(id: str,tool: str=Form(),file: UploadFile=None):
        if file is None:
            raise ValueError('Native output file required')
        raw = await file.read(4*1024*1024+1)
        store.ingest(id,tool,raw)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/findings/{finding}/risk')
    def risk_context(id: str, finding: str, exposure: str=Form(), asset_impact: str=Form(), exploitability: str=Form(), evidence_ids: str=Form(''), note: str=Form(), actor: str=Form()):
        refs=[s.strip() for s in evidence_ids.split(',') if s.strip()]
        if len(refs)>20:
            raise ValueError('At most 20 observation references are accepted')
        store.set_risk_context(id,finding,exposure,asset_impact,exploitability,refs,note,actor)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/findings/{finding}/review')
    def review(id: str, finding: str, disposition: str=Form(), note: str=Form(), actor: str=Form(), evidence_digest: str=Form()):
        store.review_finding(id,finding,disposition,note,actor,evidence_digest)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/observations/{observation}/adopt')
    def adopt(id: str, observation: str):
        store.adopt_observation(id,observation)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/report-draft')
    def draft(id: str):
        draft_report(store,id)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.post('/assessments/{id}/report-draft/review')
    def accept_draft(id: str, draft_id: str=Form(), basis: str=Form(), actor: str=Form(), note: str=Form()):
        review_draft(store,id,draft_id,basis,actor,note)
        return RedirectResponse(f'/assessments/{id}',303)

    @app.get('/assessments/{id}/report.pdf')
    def report(id: str):
        return Response(generate(store,id),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="coverageproof-{id}.pdf"'})

    @app.get('/assessments/{id}/evidence/{artifact}')
    def evidence(id: str,artifact: str):
        with store.tx() as db:
            row = db.execute('SELECT raw FROM artifacts WHERE id=? AND assessment=?',(artifact,id)).fetchone()
        if not row:
            raise HTTPException(404)
        return Response(row['raw'],media_type='application/octet-stream',headers={'Content-Disposition':f'attachment; filename="evidence-{artifact}.bin"'})
    return app

app = create_app()
