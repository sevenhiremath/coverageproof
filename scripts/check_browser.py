"""Owned browser integration test, development planning and a synthetic report draft.

No real model/scanner is called. Chromium visits our loopback app and fixture only.
"""
import hashlib
import importlib
from io import BytesIO
import json
import os
from pathlib import Path
import runpy
import time
from http.server import ThreadingHTTPServer
from threading import Thread

import httpx
from playwright.sync_api import sync_playwright, expect
from pypdf import PdfReader
import uvicorn


OUT=Path(os.environ.get('BROWSER_OUTPUT','output/browser-check'))
OUT.mkdir(parents=True,exist_ok=True)
FIXTURE_PORT=8765
BASE='http://127.0.0.1:8000'
TEST_TEXT='Automated test draft: this fixture response lacked the expected nosniff header.'


def main():
    fixture_class=runpy.run_path('local-lab/fixture.py')['Fixture']
    fixture=ThreadingHTTPServer(('127.0.0.1',FIXTURE_PORT),fixture_class)
    Thread(target=fixture.serve_forever,daemon=True).start()
    app_module=importlib.import_module('coverageproof.app')
    narrative=importlib.import_module('coverageproof.narrative')

    class SyntheticReportProvider:
        def structured(self,schema,prompt,context):
            root=next(c for c in context['checks'] if c['action']['target'].endswith('/'))
            statement={'text':TEST_TEXT,'check_ids':[root['id']],'evidence_ids':[root['observations'][0]['id']]}
            return json.dumps({'mode':'model','executive_summary':[statement],
                'limitations':[dict(statement,text='Automated test draft: other vulnerability classes remain unassessed.')]})

    # Inject only a test provider at the HTTP application boundary. No production test route exists.
    app_module.draft_report=lambda store,id:narrative.draft_report(store,id,SyntheticReportProvider())
    app=app_module.create_app()
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8000,log_level='warning'))
    thread=Thread(target=server.run,daemon=True);thread.start()
    summary={'source':'automated owned Chromium integration test','planning_mode':'development',
        'report_provider':'synthetic test provider, not live AI','source_commit':os.environ.get('COVERAGEPROOF_SOURCE_COMMIT'),
        'checks':[],'status':'running'}
    page=None
    try:
        with httpx.Client(trust_env=False) as client:
            for attempt in range(100):
                try:
                    if client.get(BASE+'/health').status_code==200:break
                except httpx.HTTPError:pass
                time.sleep(.05)
            else:raise AssertionError('Owned application did not start')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,chromium_sandbox=False)
            summary['browser']=browser.version
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();page.set_default_timeout(15000)
            page_errors=[];page.on('pageerror',lambda e:page_errors.append(str(e)))
            page.goto(BASE)
            page.locator('[name=request_text]').fill('Automated browser test: assess root and admin headers; report prose is a synthetic test fixture.')
            scope={'name':'Owned browser test fixture','networks':['127.0.0.1/32'],'ports':[FIXTURE_PORT],
                'authorization_reference':'Self-owned isolated browser test fixture; not organizer authorization'}
            page.locator('[name=scope_json]').fill(json.dumps(scope))
            page.get_by_role('button',name='Create assessment',exact=True).click()
            page.wait_for_url('**/assessments/*')
            assessment=page.url.rsplit('/',1)[1]
            assessment_url=page.url

            def state():
                response=context.request.get(BASE+f'/api/assessments/{assessment}')
                assert response.ok
                return response.json()

            def add_check(path):
                page.get_by_text('Add an explicit registered check',exact=True).click()
                page.locator('[name=action_json]').fill(json.dumps({'check':'header-nosniff','target':f'http://127.0.0.1:{FIXTURE_PORT}{path}','scope_revision':1}))
                page.get_by_role('button',name='Add check',exact=True).click()
                expect(page.get_by_role('heading',name='Coverage and unresolved gaps',exact=True)).to_be_visible()

            def execute(check):
                form=page.locator(f'form[action="/checks/{check}/approve"]')
                form.locator('[name=actor]').fill('Automated browser test')
                form.get_by_role('button',name='Approve this HTTP check',exact=True).click()
                form=page.locator(f'form[action="/checks/{check}/execute"]')
                form.get_by_role('button',name='Execute approved check',exact=True).click()
                expect(page.get_by_role('heading',name='Coverage and unresolved gaps',exact=True)).to_be_visible()

            def pdf_text(filename):
                with page.expect_download() as download:
                    page.get_by_role('link',name='Download assessment PDF',exact=True).click()
                path=OUT/filename;download.value.save_as(path)
                return ' '.join(' '.join(p.extract_text() for p in PdfReader(path).pages).split())

            add_check('/');add_check('/admin')
            snap=state();root,admin=[c['id'] for c in snap['checks']]
            assert all(c['state']=='unattempted' for c in snap['checks'])
            execute(root)
            assessment_summary=page.get_by_role('region',name='What does this assessment establish?',exact=True)
            expect(assessment_summary.get_by_text('1 unanswered checks',exact=True)).to_be_visible()
            expect(assessment_summary.get_by_text('1 answered conditions',exact=True)).to_be_visible()
            snap=state()
            assert len(snap['findings'])==1 and snap['checks'][1]['state']=='unattempted'
            summary['before_followup_states']=[c['state'] for c in snap['checks']]
            before_count=len(snap['findings'])
            page.screenshot(path=str(OUT/'before-followup.png'),full_page=True)
            summary['checks'].append('Root execution preserves the unattempted admin gap')
            page.get_by_role('button',name='Review gaps and propose checks',exact=True).click()
            snap=state();decision=next(e['payload'] for e in reversed(snap['events']) if e['kind']=='planning_decision')
            assert decision['mode']=='development' and decision['checks'][0]['action']==snap['checks'][1]['action']
            assert decision['checks'][0]['evidence_ids']
            execute(admin)
            expect(assessment_summary.get_by_text('0 unanswered checks',exact=True)).to_be_visible()
            expect(assessment_summary.get_by_text('2 answered conditions',exact=True)).to_be_visible()
            expect(assessment_summary.get_by_text('Every declared check has an interpretable result or an applicability review. This does not establish that the system is secure.',exact=True)).to_be_visible()
            snap=state()
            assert len(snap['findings'])==1 and snap['checks'][1]['state']=='condition_not_observed'
            assert all(a['consumed'] for a in snap['approvals'])
            summary['after_followup_states']=[c['state'] for c in snap['checks']]
            summary['issue_counts_before_after']=[before_count,len(snap['findings'])]
            page.screenshot(path=str(OUT/'after-followup.png'),full_page=True)
            summary['checks'].append('Proposed admin follow-up needs approval and updates only its declared condition')

            artifact=snap['artifacts'][0]
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Evidence artifacts',exact=True))
            with page.expect_download() as download:section.get_by_role('link').first.click()
            evidence=OUT/'owned-http-evidence.bin';download.value.save_as(evidence)
            assert hashlib.sha256(evidence.read_bytes()).hexdigest()==artifact['sha256']
            summary['checks'].append('Browser evidence download matches stored SHA256')

            page.get_by_role('button',name='Draft evidence-linked report explanations',exact=True).click()
            expect(page.get_by_text(TEST_TEXT,exact=True)).to_be_visible()
            assert 'test_provider' in page.locator('body').inner_text()
            assert TEST_TEXT not in pdf_text('before-draft-acceptance.pdf')
            form=page.locator(f'form[action="/assessments/{assessment}/report-draft/review"]')
            form.locator('[name=actor]').fill('Automated test reviewer (not human sign-off)')
            form.locator('[name=note]').fill('Synthetic draft review to test the interface; not a live AI or client report.')
            form.get_by_role('button',name='Accept these explanations for the report',exact=True).click()
            assert TEST_TEXT in pdf_text('accepted-test-draft.pdf')
            add_check('/unassessed')
            expect(page.get_by_text('Assessment changed. This draft is excluded from the PDF; generate and review a current draft.',exact=True)).to_be_visible()
            assert TEST_TEXT not in pdf_text('after-draft-invalidation.pdf')
            summary['checks'].append('Unaccepted and outdated synthetic report drafts stay out of downloaded PDF')

            page.get_by_text('Add an explicit registered check',exact=True).click()
            page.locator('[name=action_json]').fill(json.dumps({'check':'header-nosniff','target':'http://127.0.0.2:8765/','scope_revision':1}))
            page.get_by_role('button',name='Add check',exact=True).click()
            expect(page.get_by_text('Target outside approved networks',exact=True)).to_be_visible()
            page.goto(assessment_url)
            assert len(state()['checks'])==3
            summary['checks'].append('Out-of-scope action blocked without a target request')
            page.screenshot(path=str(OUT/'after-draft-invalidation.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile layout overflows horizontally'
            assert not page_errors,page_errors
            summary.update(status='passed',page_errors=page_errors,final_states=[c['state'] for c in state()['checks']])
            browser.close()
    except Exception as error:
        summary.update(status='failed',error_type=type(error).__name__,error=str(error)[:2000])
        if page:
            try:page.screenshot(path=str(OUT/'failure.png'),full_page=True)
            except Exception:pass
        raise
    finally:
        (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        server.should_exit=True;thread.join(timeout=5)
        fixture.shutdown();fixture.server_close()

if __name__=='__main__':main()
