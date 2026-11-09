from io import BytesIO
from fastapi.testclient import TestClient
from pypdf import PdfReader
from coverageproof.app import create_app
from coverageproof.domain import Action,Receipt,State,now
from coverageproof.report import generate


def test_unanswered_count_keeps_failure_and_applicability_separate(store,scope):
    a=store.create('Understand the declared assessment gaps',scope)
    ids=[store.add_check(a,Action(check='header-nosniff',target=f'http://127.0.0.1:8765/{path}',scope_revision=1)) for path in ['', 'admin','failed','excluded-method']]
    attempt,_,_=store.claim(ids[0],store.approve(ids[0],'Unit analyst'))
    store.finish(attempt,'completed','Unit fixture receipt',b'unit fixture',Receipt(target='http://127.0.0.1:8765/',check='header-nosniff',outcome=State.NOT_OBSERVED,detail='Synthetic unit receipt only',source_ref='unit',observed_at=now()))
    attempt,_,_=store.claim(ids[2],store.approve(ids[2],'Unit analyst'))
    store.finish(attempt,'timeout','Synthetic timeout injection')
    store.set_applicability(ids[3],'not_applicable','Owner excludes this path from the selected header methodology','Unit analyst')
    snap=store.snapshot(a);summary=snap['coverage_summary']
    assert (summary['declared_total'],summary['answered_total'],summary['unanswered_total'],summary['not_applicable_total'])==(4,1,2,1)
    assert {g['state'] for g in summary['gaps']}=={'unattempted','failed'}
    assert summary['gaps'][0]['check_id']==ids[1]
    text=' '.join(' '.join(p.extract_text() for p in PdfReader(BytesIO(generate(store,a))).pages).split())
    assert '2 unanswered declared check(s)' in text
    with TestClient(create_app(store.path)) as client:
        html=client.get(f'/assessments/{a}').text
        assert '2 unanswered declared check(s)' in html
        assert 'No matching observation or execution attempt' in html
        assert f'href="#check-{ids[1]}"' in html


def test_report_embeds_licensed_fonts_and_document_metadata(store,scope):
    a=store.create('Portable English report with traceable evidence',scope)
    pdf=PdfReader(BytesIO(generate(store,a)))
    embedded=[]
    for page in pdf.pages:
        for ref in page['/Resources']['/Font'].values():
            font=ref.get_object()
            descriptor=font.get('/FontDescriptor')
            if descriptor and descriptor.get_object().get('/FontFile2'):
                embedded.append(descriptor.get_object()['/FontFile2'].get_data())
    assert embedded
    assert all(b'Copyright (c) 2003 by Bitstream' in data and b'Permission is hereby granted' in data for data in embedded)
    assert pdf.metadata.title=='CoverageProof VAPT assessment'
    assert pdf.metadata.author=='CoverageProof'
