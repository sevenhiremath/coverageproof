"""Bounded private model output; public audit metadata contains no response prose."""
import json
from pathlib import Path
import sqlite3
from pydantic import ValidationError


PUBLIC_FIELDS = {'mode','explanation','checks','action','check','target','port','scope_revision','rationale',
    'evidence_ids','alternatives','tool','reason_not_chosen','drawback','executive_summary','limitations','text','check_ids'}


def safe_errors(error):
    if not isinstance(error,ValidationError):
        return [{'type':type(error).__name__}]
    return [{'location':[part if isinstance(part,int) or part in PUBLIC_FIELDS else '<field>' for part in item['loc']],
        'type':item['type']} for item in error.errors(include_input=False,include_url=False)[:12]]


def public_validation_failure(error, call):
    fields=', '.join('.'.join(map(str,item.get('location',[])))+':'+item['type'] for item in safe_errors(error))
    return ValueError(f'Model output failed validation ({fields}). Private model call: {call}. No fallback or action execution occurred.')


def record_call(store, assessment, purpose, provider, outcome, error=None):
    trace=getattr(provider,'trace',None)
    if trace is None:
        return None  # Development mode or a unit-test provider did not make an HTTP call.
    metadata=dict(trace)
    metadata['outcome']=outcome
    if error is not None:
        metadata['validation_errors']=safe_errors(error)
    return store.record_model_call(assessment,purpose,metadata,getattr(provider,'raw_output',b''))


def export_calls(database, destination, assessment=None):
    database=Path(database)
    if not database.is_file():
        raise ValueError('Existing assessment database required')
    with sqlite3.connect(f'{database.resolve().as_uri()}?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        query='SELECT * FROM model_calls'
        args=()
        if assessment:
            query+=' WHERE assessment=?';args=(assessment,)
        rows=db.execute(query+' ORDER BY rowid LIMIT 101',args).fetchall()
    if len(rows)>100:
        raise ValueError('More than 100 calls; select a single assessment')
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=False)
    manifest=[]
    for row in rows:
        output=f'{row["id"]}.output.txt'
        (destination/output).write_bytes(row['raw_output'])
        manifest.append({'id':row['id'],'assessment':row['assessment'],'purpose':row['purpose'],
            'created':row['created'],'metadata':json.loads(row['metadata']),'output_file':output})
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return len(manifest)

