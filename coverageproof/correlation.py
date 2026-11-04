"""Small explicit correlation rules; raw receipts always keep their original meaning."""
from hashlib import sha256
from .domain import Receipt, State, canonical_target

SEVERITY_ORDER = {'critical':0,'high':1,'medium':2,'low':3,'informational':4,'unknown':5}
NOSNIFF = 'header:x-content-type-options'


def issue_identity(receipt):
    # Nikto plugin IDs can cover several unrelated conditions (e.g. 013587).
    # Derive grouping from the exact preserved message as well as its source ID.
    # Apply at read time so previously imported artifacts need no rewriting.
    if receipt.issue_class and receipt.issue_class.startswith('nikto:'):
        import json
        message_hash = sha256(json.dumps([receipt.http_method, receipt.detail], ensure_ascii=False).encode('utf-8')).hexdigest()
        return (f'{receipt.issue_class}:message:{message_hash}',
                'Same Nikto source ID, recorded method and exact message on the same endpoint; missing methods remain unknown. Plugin ID alone does not identify a condition. No cross-tool mapping or exploitability inference.')
    # ZAP's documented passive rule 10021 checks this exact header condition.
    # Only GET without a parameter maps onto the registered HTTP GET check.
    if receipt.issue_class == 'zap:10021:GET:':
        return NOSNIFF, 'ZAP passive rule 10021 and the HTTP GET header check concern the same response-header condition.'
    if receipt.check == 'header-nosniff':
        return NOSNIFF, 'Registered check for X-Content-Type-Options on one HTTP GET response.'
    return receipt.issue_class, 'Exact source issue identifier; no title, CVE-only or fuzzy matching.'


def correlate(rows):
    """Rows carry observation id, artifact id, source tool and a Receipt.

    Negative receipts can contradict an existing case; they never create an issue.
    """
    cases = {}
    for row in rows:
        r = row['receipt']
        issue, reason = issue_identity(r)
        if not issue or r.outcome != State.FINDING:
            continue
        key = (canonical_target(r.target)[0],issue)
        case = cases.setdefault(key, {
            'id':sha256(repr(key).encode()).hexdigest()[:12], 'asset':key[0],
            'issue_class':issue, 'title':r.title or issue, 'severity':'unknown',
            'confidence':r.confidence, 'status':'suspected; analyst review required',
            'evidence':[], 'source_observations':[], 'source_tools':[],
            'source_issue_classes':[], 'source_severities':[], 'source_confidences':[],
            'correlation_reasons':[], 'validation_status':'source_reported',
            'severity_disagreement':False, 'cvss':None,
            'remediation':r.remediation or 'Review the source evidence and confirm applicability before selecting remediation.',
            'impact':'Not independently established; depends on affected asset and validation.',
        })
    # Keep all related positive/negative observations, including disagreements.
    for row in rows:
        r = row['receipt']
        issue, reason = issue_identity(r)
        if not issue or r.outcome not in {State.FINDING,State.NOT_OBSERVED}:
            continue
        key=(canonical_target(r.target)[0],issue)
        if key not in cases:
            continue
        f=cases[key]
        f['evidence'].append({'observation':row['id'],'artifact':row['artifact'],'source_ref':r.source_ref})
        f['source_observations'].append({'id':row['id'],'tool':row['tool'],'source_issue_class':r.issue_class,'outcome':str(r.outcome),'severity':r.severity,'confidence':r.confidence,'observed_at':r.observed_at,'detail':r.detail,'source_ref':r.source_ref,'http_method':r.http_method})
        for field,value in [('source_tools',row['tool']),('source_issue_classes',r.issue_class or r.check),('correlation_reasons',reason),('source_severities',r.severity),('source_confidences',r.confidence)]:
            if value not in f[field]:f[field].append(value)
        if r.outcome==State.FINDING and SEVERITY_ORDER.get(r.severity,5)<SEVERITY_ORDER[f['severity']]:
            f['severity']=r.severity
        if r.remediation and f['remediation'].startswith('Review the source evidence'):
            f['remediation']=r.remediation
    for f in cases.values():
        outcomes={o['outcome'] for o in f['source_observations']}
        if {str(State.FINDING),str(State.NOT_OBSERVED)}<=outcomes:
            f['validation_status']='conflicting_observations'
        known={o['severity'] for o in f['source_observations'] if o['outcome']==State.FINDING and o['severity']!='unknown'}
        f['severity_disagreement']=len(known)>1
        f['confidence']='; '.join(f['source_confidences'])
        f['correlation_limit']='Same endpoint and issue condition; timing, response variants and scanner configuration can still explain differing observations. No majority vote or exploitability inference.'
    return list(cases.values())


def risk_key(f):
    context=f.get('risk_context') or {}
    return (SEVERITY_ORDER.get(f['severity'],5),
        {'external_per_owner':0,'internal_per_owner':1,'lab_only':2,'unknown':3}.get(context.get('exposure'),3),
        {'high':0,'medium':1,'low':2,'unknown':3}.get(context.get('asset_impact'),3),
        {'analyst_validated':0,'not_assessed':1}.get(context.get('exploitability'),1),
        f['asset'],f['id'])


def explain_risk(f):
    c=f.get('risk_context') or {}
    known=sorted({o['severity'] for o in f['source_observations'] if o['outcome']==State.FINDING and o['severity']!='unknown'})
    return {
        'method':'Source severity first, then analyst-declared exposure, asset impact and validation. Asset/id break remaining ties. No numeric risk score.',
        'severity_reason':f'Highest supplied finding severity is {f["severity"]}; supplied values: {known or ["unknown"]}. Source differences remain visible.',
        'exposure':c.get('exposure','unknown'), 'asset_impact':c.get('asset_impact','unknown'),
        'exploitability':c.get('exploitability','not_assessed'),
        'confidence':'Source confidence labels are retained without numerical conversion or cross-tool averaging.',
        'limitations':'Analyst context is an attributed assessment, not independent verification. A high source severity can still be a false positive.',
    }
