from collections import Counter
from hashlib import sha256
from html import escape
from io import BytesIO
import json
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from .domain import now
from .store import uid


def render(snapshot):
    stream = BytesIO()
    styles = getSampleStyleSheet()
    font_root = Path('/usr/share/fonts/truetype/dejavu')
    if (font_root / 'DejaVuSans.ttf').exists():
        pdfmetrics.registerFont(TTFont('CoverageSans', str(font_root / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont('CoverageSansBold', str(font_root / 'DejaVuSans-Bold.ttf')))
        for name in ['BodyText','Normal','Title','Heading1','Heading2']:
            styles[name].fontName = 'CoverageSansBold' if name in ['Title','Heading1','Heading2'] else 'CoverageSans'
    styles['Heading1'].keepWithNext = True
    styles['Heading2'].keepWithNext = True
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 13
    story = []
    def p(text, style='BodyText'):
        story.append(Paragraph(escape(str(text)).replace('\n','<br/>'), styles[style]))
        if style not in {'Heading1','Heading2','Title'}:
            story.append(Spacer(1, 5))
    p('CoverageProof | VAPT assessment', 'Title')
    p(f'Assessment {snapshot["id"]} | Snapshot {snapshot["snapshot_id"]}', 'BodyText')
    p('Executive summary', 'Heading1')
    p(snapshot['request'])
    p(f'{len(snapshot["findings"])} normalized issue candidates; {len(snapshot["checks"])} declared checks. Candidates are suspected until reviewed. An open TCP service is discovery, not a vulnerability. This report does not establish that any asset is secure.')
    summary = snapshot.get('coverage_summary')
    if summary:
        p(f'{summary["unanswered_total"]} unanswered declared check(s); {summary["answered_total"]} conditions with interpretable receipts; {summary["not_applicable_total"]} marked not applicable. Counts refer only to this plan.')
    draft = snapshot.get('report_draft')
    if draft and draft['current'] and draft['review']:
        p('AI-assisted explanation reviewed by the analyst' if draft['event']['payload']['provider']=='ollama' else 'Synthetic report draft for automated tests (not live AI)', 'Heading2')
        p(f'Reviewed by {draft["review"]["payload"]["actor"]}; {draft["review"]["created"]}. These explanations do not replace the authoritative check states below.')
        p('Review reason: ' + draft['review']['payload']['note'])
        for section in ('executive_summary','limitations'):
            for item in draft['event']['payload']['draft'][section]:
                p(item['text'])
                p(f'Checks: {item["check_ids"]}; observations: {item["evidence_ids"]}')
    else:
        p('AI report explanations: no current analyst-accepted draft. The stored assessment state is reported below.')
    p('Assessment methodology and rules of engagement', 'Heading1')
    p('Coverage is limited to the explicitly declared checks. Literal-IP network boundaries and permitted ports are enforced. All runner actions need one-use approval. Redirects and environment proxies are disabled for the supported HTTP runner. Native findings-only exports cannot establish negative checks.')
    p(json.dumps(snapshot['scope'], indent=2))
    p('Tool execution and assets tested', 'Heading1')
    for c in snapshot['checks']:
        p(f'{c["id"]} | {c["action"]["target"]} | {c["condition"]} | {c["state"]}')
        if c.get('applicability'):
            p('Applicability review: ' + json.dumps(c['applicability']))
        for a in c['attempts']:
            p(f'Execution {a["id"]}: {a["status"]}; {a["created"]}; {a["detail"]}')
    for a in snapshot['artifacts']:
        p(f'Artifact {a["id"]}: {a["tool"]}, source={a["mode"]}, ingested={a["created"]}, SHA256={a["sha256"]}')
    p('Finding review summary', 'Heading1')
    p(json.dumps(dict(Counter(f['status'] for f in snapshot['findings']))))
    p('All candidates, including false-positive decisions, remain below for traceability. An accepted-for-report decision is analyst judgment, not proof of exploitation. New evidence makes earlier reviews outdated.')
    if snapshot.get('unmatched'):
        p('Imported observations not yet in the declared plan', 'Heading2')
        for o in snapshot['unmatched']:
            p(f'{o["id"]} | {o["receipt"]["target"]} | {o["receipt"]["check"]} | artifact {o["artifact"]}: {o["receipt"]["detail"]}')
        p('These observations do not count as completed declared checks until the analyst reviews and adds them to the plan.')
    p('Severity distribution and prioritization', 'Heading1')
    p(json.dumps(dict(Counter(f['severity'] for f in snapshot['findings'] if f['status'] != 'false_positive'))))
    p('Ranking uses the highest supplied source severity, then attributed exposure, asset impact and analyst validation. Asset and finding identifier break ties. Missing inputs stay unknown. No numerical confidence, CVSS or combined risk score is invented. False-positive candidates are excluded from the active severity distribution but retained in the evidence record.')
    p('Detailed vulnerability findings, impact and remediation', 'Heading1')
    if not snapshot['findings']:
        p('No issue candidates recorded. This is not evidence that unattempted or inconclusive checks found no issues.')
    for f in snapshot['findings']:
        p(f'{f["id"]} | {f["title"]}', 'Heading2')
        for key in ('asset','issue_class','severity','cvss','confidence','status','impact','remediation'):
            p(f'{key}: {f[key]}')
        if f.get('validation_status'):
            p(f'Evidence status: {f["validation_status"]}; freshness: {f.get("freshness_status", "unknown")}; source tools: {", ".join(f["source_tools"])}')
            p(f['correlation_limit'])
            if f['severity_disagreement']:
                p(f'Source severity disagreement: {f["source_severities"]}. The highest supplied severity is displayed, not an independently calculated score.')
            for source in f['source_observations']:
                p(f'{source["tool"]} | {source["outcome"]} | {source["observed_at"]} | observation {source["id"]}: {source["detail"]}')
            p(json.dumps(f['risk_explanation']))
            if f.get('risk_context'):
                p(f'Risk context by {f["risk_context"]["actor"]} at {f["risk_context"]["created"]}: {f["risk_context"]["note"]}')
        if f.get('review'):
            p(f'Last review by {f["review"]["actor"]} at {f["review"]["created"]}: {f["review"]["note"]}')
        p('CVE/CWE: not independently established. References: native artifact and source pointers below.')
        for e in f['evidence']:
            p(json.dumps(e))
    p('Evidence and coverage limitations', 'Heading1')
    for c in snapshot['checks']:
        p(f'{c["action"]["target"]} | {c["state"]}', 'Heading2')
        for o in c['observations']:
            p(f'Collection freshness: {o.get("freshness", {}).get("state", "unknown")}')
            p(f'{o["id"]} / {o["artifact"]} {o["receipt"]["source_ref"]}: {o["receipt"]["detail"]}; observed={o["receipt"]["observed_at"]}')
    p('Assumptions, failures, approvals and timestamps', 'Heading1')
    p('Analyst-supplied imports are not live executions or authenticated attestations. Schema-valid input alone does not establish origin. Scope revisions make earlier plans stale. Import timestamps are preserved, but timestamps outside the scope-defined evidence window are marked stale, and unknown or future timestamps remain explicit limitations. Organizer evaluation authorization must be supplied separately from the self-owned development scope.')
    p(f'Assessment created {snapshot["created"]}; report snapshot {snapshot["generated"]}. Model reasoning and reviewer sign-off status must be verified before client delivery.')
    for a in snapshot['approvals']:
        p(json.dumps(a))
    for e in snapshot['events']:
        if e['kind'] in {'action_denied','execution_denied','planning_decision','planning_failed','execution_finished','finding_reviewed','imported_observation_adopted','risk_context_recorded','applicability_reviewed','model_call_recorded'}:
            p(f'{e["created"]} {e["kind"]}: {json.dumps(e["payload"])}')
    def footer(canvas, doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#556171'))
        canvas.drawString(0.65*inch,0.4*inch,'CoverageProof | Bounded assessment | Analyst review required')
        canvas.drawRightString(7.6*inch,0.4*inch,f'Page {doc.page}')
    SimpleDocTemplate(stream, rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=44).build(story,onFirstPage=footer,onLaterPages=footer)
    return stream.getvalue()


def generate(store, assessment):
    snapshot = store.snapshot(assessment)
    snapshot.update(snapshot_id=uid(), generated=now())
    raw = render(snapshot)
    with store.tx() as db:
        db.execute('INSERT INTO reports VALUES(?,?,?,?,?)', (snapshot['snapshot_id'],assessment,json.dumps(snapshot),sha256(raw).hexdigest(),snapshot['generated']))
    return raw
