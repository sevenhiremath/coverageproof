"""Evaluate up to six frozen Store cases; no approval, execution, or retries."""
import argparse
import hashlib
import json
from pathlib import Path
from .planner import GroqProvider, model_context, validate_proposal
from .store_eval import request_aware


def run(cases_path, expected_sha256, output, live=False, provider_factory=GroqProvider):
    data=cases_path.read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise ValueError('Frozen cases SHA256 mismatch')
    suite=json.loads(data)
    if not isinstance(suite,list) or not 1 <= len(suite) <= 6:
        raise ValueError('Expected one to six frozen cases')
    if len({c['id'] for c in suite}) != len(suite):
        raise ValueError('Duplicate case IDs')
    # Check every model input before any provider call. Refuse the flawed v1 freeze.
    for case in suite:
        if 'ignore the analyst' not in json.dumps(model_context(case['snapshot'])):
            raise ValueError('Untrusted instruction missing from model input')
    output.mkdir(parents=True,exist_ok=False)
    (output/'cases.json').write_bytes(data)
    summary=dict(suite_sha256=actual,live=live,provider_calls=0,target_requests=0,
                 status='running',total_cases=len(suite),rows=[])
    for index,case in enumerate(suite):
        snap=case['snapshot']
        expected=case['expected_candidate_ids']
        baseline=request_aware(snap)
        row=dict(id=case['id'],expected=expected,request_aware=baseline,
                 baseline_pass=baseline==expected)
        if live:
            provider=provider_factory()
            summary['provider_calls']+=1
            try:
                proposal=provider.propose(snap)
                row['proposal']=proposal.model_dump(mode='json')
                validate_proposal(proposal,snap)
                selected=[c.candidate_id for c in proposal.checks]
                row.update(valid=True,selected=selected,selection_pass=selected==expected)
            except ValueError as error:
                row.update(valid=False,selection_pass=False,error_type=type(error).__name__)
            finally:
                row['trace']=getattr(provider,'trace',{})
                # Numeric names avoid treating case IDs as filesystem paths.
                (output/f'{index+1:02d}.output.txt').write_bytes(getattr(provider,'raw_output',b''))
            row['explanation_review']='pending: citation meaning, abstention, alternatives, limitations'
        summary['rows'].append(row)
        stop=live and row.get('trace',{}).get('http_status')!=200
        summary['status']='stopped_provider_failure' if stop else 'running'
        (output/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
        if stop:break
    if summary['status']=='running':summary['status']='completed'
    summary['unattempted_cases']=len(suite)-len(summary['rows'])
    (output/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--live',action='store_true',help='At most six Groq calls; stop on provider failure')
    args=parser.parse_args()
    result=run(args.cases,args.sha256,args.output,args.live)
    print(json.dumps({k:result[k] for k in ('status','provider_calls','target_requests','unattempted_cases')}))
    if result['status']!='completed':raise SystemExit(2)


if __name__=='__main__':main()
