"""Genuine owned HTTP experiment; no fabricated native scanner output."""
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from coverageproof.domain import Action, Scope
from coverageproof.store import Store
from coverageproof.runner import execute
from coverageproof.planner import plan
from coverageproof.report import generate
from coverageproof.model_diagnostics import export_calls
from coverageproof.store import uid

class Fixture(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        if self.path=='/admin': self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(b'Self-owned CoverageProof development fixture')
    def log_message(self,*args): pass

out=Path('output');out.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),Fixture)
Thread(target=server.serve_forever,daemon=True).start()
port=server.server_address[1]
store=Store(out/'experiment.sqlite')
scope=Scope(name='Owned HTTP experiment',networks=('127.0.0.1/32',),ports=(port,),authorization_reference='Self-owned Python HTTP fixture; not organizer authorization')
ids=[]
summary={'status':'running','run_id':uid(),'assessment_ids':ids,'planner_mode':None,'source':'genuine self-owned HTTP fixture; no native scanner execution'}
(out/'experiment-summary.json').write_text(json.dumps(summary,indent=2))
try:
    for label in ['A: both declared checks assessed','B: admin surface unattempted']:
        a=store.create(label,scope); ids.append(a)
        checks=[store.add_check(a,Action(check='header-nosniff',target=f'http://127.0.0.1:{port}{path}',scope_revision=1)) for path in ['/','/admin']]
        for c in checks[:2 if label.startswith('A') else 1]: execute(store,c,store.approve(c,'Owned fixture experiment'))
    before=[store.snapshot(a) for a in ids]
    assert [len(s['findings']) for s in before]==[1,1]
    assert before[1]['checks'][1]['state']=='unattempted'
    proposal=plan(store,ids[1])
    expected=before[1]['checks'][1]['action']
    assert any(p.action.model_dump()==expected for p in proposal.checks), 'Planner did not select the declared admin gap; preserve its decision and investigate'
    check=before[1]['checks'][1]['id'];execute(store,check,store.approve(check,'Owned fixture follow-up'))
    after=store.snapshot(ids[1]);assert after['checks'][1]['state']=='condition_not_observed'
    assert len(after['findings'])==1
    for a in ids:
        snapshot=store.snapshot(a)
        (out/f'{a}.json').write_text(json.dumps(snapshot,indent=2))
        for e in snapshot['artifacts']:
            with store.tx() as db: raw=db.execute('SELECT raw FROM artifacts WHERE id=?',(e['id'],)).fetchone()['raw']
            (out/f'{e["id"]}.http').write_bytes(raw)
    (out/'sample-vapt.pdf').write_bytes(generate(store,ids[1]))
    summary.update({'status':'completed','sample_size':2,'check':'one response X-Content-Type-Options condition per exact URL','source':'genuine self-owned HTTP fixture, not native scanner execution','baseline_counts':[1,1],'before_states':[[c['state'] for c in s['checks']] for s in before],'after_states':[c['state'] for c in after['checks']],'planner_mode':proposal.mode,'limitations':'Two scripted HTTP assessments only. No general accuracy or time-saving claim. Mandatory three-tool and live AI validation still pending.'})
    (out/'experiment-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
except Exception as error:
    summary.update(status='failed',error_type=type(error).__name__,limitations='Model/experiment failed; the declared gap remains unresolved. Inspect private model diagnostics. No fallback or follow-up substituted.')
    raise
finally:
    server.shutdown();server.server_close()
    summary['assessment_ids']=ids
    summary['report_file']='observed-state-vapt.pdf'
    summary['diagnostics_dir']=f'model-diagnostics/{summary["run_id"]}'
    if ids:
        for a in ids:
            snapshot=store.snapshot(a)
            (out/f'{a}.json').write_text(json.dumps(snapshot,indent=2))
            for artifact in snapshot['artifacts']:
                with store.tx() as db:raw=db.execute('SELECT raw FROM artifacts WHERE id=?',(artifact['id'],)).fetchone()['raw']
                (out/f'{artifact["id"]}.http').write_bytes(raw)
        (out/'observed-state-vapt.pdf').write_bytes(generate(store,ids[-1]))
        for a in ids:
            export_calls(store.path,out/'model-diagnostics'/summary['run_id']/a,a)
    (out/'experiment-summary.json').write_text(json.dumps(summary,indent=2))
