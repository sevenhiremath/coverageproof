from __future__ import annotations
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from .adapters import parse
from .correlation import correlate, risk_key, explain_risk
from .freshness import freshness
from .domain import Action, Scope, Receipt, State, CHECKS, action_fingerprint, canonical_target, coverage, digest, now, validate_scope


def uid():
    return uuid4().hex


SCHEMA = '''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS assessments(id TEXT PRIMARY KEY,request TEXT NOT NULL,scope TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS checks(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),action TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),tool TEXT NOT NULL,mode TEXT NOT NULL,sha256 TEXT NOT NULL,raw BLOB NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS observations(id TEXT PRIMARY KEY,check_id TEXT REFERENCES checks(id),artifact TEXT REFERENCES artifacts(id),receipt TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY,check_id TEXT REFERENCES checks(id),status TEXT NOT NULL,detail TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,check_id TEXT REFERENCES checks(id),fingerprint TEXT NOT NULL,actor TEXT NOT NULL,created TEXT NOT NULL,consumed TEXT);
CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),kind TEXT NOT NULL,payload TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS risk_contexts(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),finding TEXT NOT NULL,exposure TEXT NOT NULL,asset_impact TEXT NOT NULL,exploitability TEXT NOT NULL,evidence_ids TEXT NOT NULL,note TEXT NOT NULL,actor TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),finding TEXT NOT NULL,disposition TEXT NOT NULL,note TEXT NOT NULL,actor TEXT NOT NULL,evidence_digest TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS unmatched(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),artifact TEXT REFERENCES artifacts(id),receipt TEXT NOT NULL,created TEXT NOT NULL,linked_check TEXT REFERENCES checks(id));
CREATE TABLE IF NOT EXISTS applicability(id TEXT PRIMARY KEY,check_id TEXT REFERENCES checks(id),decision TEXT NOT NULL,note TEXT NOT NULL,actor TEXT NOT NULL,basis TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_calls(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),purpose TEXT NOT NULL,metadata TEXT NOT NULL,raw_output BLOB NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reports(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),snapshot TEXT NOT NULL,sha256 TEXT NOT NULL,created TEXT NOT NULL);
'''


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.tx() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def tx(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def event(self, db, assessment, kind, payload):
        db.execute('INSERT INTO events VALUES(?,?,?,?,?)', (uid(), assessment, kind, json.dumps(payload), now()))

    def record_model_call(self, assessment, purpose, metadata, raw_output):
        if purpose not in {'planning','report_draft'} or len(raw_output)>262144:
            raise ValueError('Invalid private model diagnostic')
        call=uid()
        with self.tx() as db:
            self.context(db,assessment)
            db.execute('INSERT INTO model_calls VALUES(?,?,?,?,?,?)',(call,assessment,purpose,json.dumps(metadata),raw_output,now()))
            self.event(db,assessment,'model_call_recorded',{'model_call':call,'purpose':purpose,
                'provider':metadata['provider'],'outcome':metadata['outcome'],'elapsed_ms':metadata['elapsed_ms'],
                'output_sha256':metadata.get('output_sha256'),'validation_errors':metadata.get('validation_errors',[])})
        return call

    def create(self, request, scope):
        if not request.strip() or len(request) > 4000:
            raise ValueError('Assessment request must have 1-4000 characters')
        id = uid()
        with self.tx() as db:
            db.execute('INSERT INTO assessments VALUES(?,?,?,?)', (id, request, scope.model_dump_json(), now()))
            self.event(db, id, 'assessment_created', {'environment': scope.environment})
        return id

    def context(self, db, assessment):
        row = db.execute('SELECT * FROM assessments WHERE id=?', (assessment,)).fetchone()
        if row is None:
            raise KeyError('Assessment not found')
        return row, Scope.model_validate_json(row['scope'])

    def add_check(self, assessment, action):
        # Persist denials, even when no executable check was created.
        with self.tx() as db:
            _, scope = self.context(db, assessment)
            try:
                validate_scope(scope, action)
            except ValueError as e:
                self.event(db, assessment, 'action_denied', {'action': action.model_dump(), 'reason': str(e)})
                error = str(e)
            else:
                duplicate = db.execute('SELECT id FROM checks WHERE assessment=? AND action=?', (assessment, action.model_dump_json())).fetchone()
                if duplicate:
                    return duplicate['id']
                id = uid()
                db.execute('INSERT INTO checks VALUES(?,?,?,?)', (id, assessment, action.model_dump_json(), now()))
                self.event(db, assessment, 'check_planned', {'check_id': id, 'action': action.model_dump()})
                return id
        raise ValueError(error)

    def check_context(self, db, check_id):
        row = db.execute('SELECT * FROM checks WHERE id=?', (check_id,)).fetchone()
        if row is None:
            raise KeyError('Check not found')
        _, scope = self.context(db, row['assessment'])
        return row, scope, Action.model_validate_json(row['action'])

    def approve(self, check_id, actor):
        if not actor.strip() or len(actor) > 200:
            raise ValueError('Analyst identity required')
        with self.tx() as db:
            row, scope, action = self.check_context(db, check_id)
            fp = action_fingerprint(scope, action)
            id = uid()
            db.execute('INSERT INTO approvals VALUES(?,?,?,?,?,NULL)', (id, check_id, fp, actor, now()))
            self.event(db, row['assessment'], 'action_approved', {'approval': id, 'fingerprint': fp, 'actor': actor})
            return id

    def claim(self, check_id, approval):
        with self.tx() as db:
            row, scope, action = self.check_context(db, check_id)
            try:
                fp = action_fingerprint(scope, action)
            except ValueError as e:
                fp=None
                scope_reason=str(e)
            approved = db.execute('SELECT * FROM approvals WHERE id=? AND check_id=? AND fingerprint=? AND consumed IS NULL', (approval, check_id, fp)).fetchone()
            active = db.execute("SELECT 1 FROM attempts WHERE status='running'").fetchone()
            reason = scope_reason if fp is None else 'Approval missing, consumed or bound to another action' if approved is None else 'Runner concurrency limit (one job) reached' if active else None
            applicability = db.execute('SELECT * FROM applicability WHERE check_id=? ORDER BY rowid DESC LIMIT 1', (check_id,)).fetchone()
            has_results = db.execute('SELECT 1 FROM observations WHERE check_id=?', (check_id,)).fetchone() or db.execute('SELECT 1 FROM attempts WHERE check_id=?', (check_id,)).fetchone()
            if applicability and not has_results and applicability['decision']=='not_applicable' and applicability['basis']==fp:
                reason = 'Check is marked not applicable; review applicability before execution'
            if reason:
                self.event(db, row['assessment'], 'execution_denied', {'check_id': check_id, 'reason': reason})
            else:
                db.execute('UPDATE approvals SET consumed=? WHERE id=?', (now(), approval))
                attempt = uid()
                db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)', (attempt, check_id, 'running', 'Approved runner action claimed', now()))
                self.event(db, row['assessment'], 'execution_started', {'attempt': attempt, 'check_id': check_id})
                return attempt, scope, action
        raise ValueError(reason)

    def finish(self, attempt, status, detail, raw=None, receipt=None):
        if status not in {'completed', 'failed', 'timeout', 'unsupported'}:
            raise ValueError('Invalid terminal execution status')
        with self.tx() as db:
            a = db.execute('SELECT * FROM attempts WHERE id=? AND status=?', (attempt, 'running')).fetchone()
            if a is None:
                raise ValueError('Attempt is not running')
            row, scope, action = self.check_context(db, a['check_id'])
            db.execute('UPDATE attempts SET status=?,detail=? WHERE id=?', (status, detail, attempt))
            if raw is not None:
                artifact = uid()
                db.execute('INSERT INTO artifacts VALUES(?,?,?,?,?,?,?)', (artifact, row['assessment'], CHECKS[action.check]['tool'], 'live', sha256(raw).hexdigest(), raw, now()))
                if receipt:
                    db.execute('INSERT INTO observations VALUES(?,?,?,?)', (uid(), row['id'], artifact, receipt.model_dump_json()))
            self.event(db, row['assessment'], 'execution_finished', {'attempt': attempt, 'status': status, 'detail': detail})

    def ingest(self, assessment, tool, raw):
        try:
            return self._ingest(assessment, tool, raw)
        except ValueError as e:
            with self.tx() as db:
                self.context(db, assessment)
                self.event(db, assessment, 'import_denied', {'tool':tool, 'sha256':sha256(raw).hexdigest(), 'reason':str(e)})
            raise

    def _ingest(self, assessment, tool, raw):
        receipts = parse(tool, raw)
        with self.tx() as db:
            _, scope = self.context(db, assessment)
            # Reject the complete import if any record violates scope; no partial ingestion.
            for r in receipts:
                kind, *port = r.check.split(':')
                validate_scope(scope, Action(check=kind, target=r.target, port=int(port[0]) if port else None, scope_revision=scope.revision))
            artifact = uid()
            db.execute('INSERT INTO artifacts VALUES(?,?,?,?,?,?,?)', (artifact, assessment, tool, 'import', sha256(raw).hexdigest(), raw, now()))
            plans = db.execute('SELECT * FROM checks WHERE assessment=?', (assessment,)).fetchall()
            for r in receipts:
                matched = False
                for c in plans:
                    action = Action.model_validate_json(c['action'])
                    expected = f'tcp-port:{action.port}' if action.check == 'tcp-port' else action.check
                    if expected == r.check and canonical_target(action.target)[0] == canonical_target(r.target)[0]:
                        db.execute('INSERT INTO observations VALUES(?,?,?,?)', (uid(), c['id'], artifact, r.model_dump_json()))
                        matched = True
                if not matched:
                    db.execute('INSERT INTO unmatched VALUES(?,?,?,?,?,NULL)', (uid(), assessment, artifact, r.model_dump_json(), now()))
            self.event(db, assessment, 'artifact_imported', {'artifact': artifact, 'tool': tool, 'parsed_receipts': len(receipts), 'source': 'analyst-supplied native output; authenticity not independently attested'})
            return artifact

    def snapshot(self, assessment):
        with self.tx() as db:
            row, scope = self.context(db, assessment)
            checks, observation_rows = [], []
            tools={a["id"]:a["tool"] for a in db.execute("SELECT id,tool FROM artifacts WHERE assessment=?",(assessment,))}
            for c in db.execute('SELECT * FROM checks WHERE assessment=? ORDER BY created,id', (assessment,)).fetchall():
                action = Action.model_validate_json(c['action'])
                observations = [dict(x) for x in db.execute('SELECT * FROM observations WHERE check_id=?', (c['id'],))]
                receipts = [Receipt.model_validate_json(o['receipt']) for o in observations]
                attempts = [dict(x) for x in db.execute('SELECT * FROM attempts WHERE check_id=?', (c['id'],))]
                for o,r in zip(observations,receipts):
                    o['freshness']=freshness(r.observed_at,scope.evidence_max_age_hours)
                usable=[]
                for o,r in zip(observations,receipts):
                    if o['freshness']['state'] in {'stale','future_timestamp'}:
                        continue
                    # A timestamp-less negative is not a current, bounded negative receipt.
                    if o['freshness']['state']=='unknown' and r.outcome==State.NOT_OBSERVED:
                        usable.append(r.model_copy(update={'outcome':State.INCONCLUSIVE}))
                    else:
                        usable.append(r)
                state = coverage(usable, stale=action.scope_revision != scope.revision)
                if receipts and not usable:state=State.STALE
                if attempts and state == State.UNATTEMPTED:
                    state = State.FAILED if attempts[-1]['status'] in {'failed','timeout','unsupported'} else State.INCONCLUSIVE
                review = db.execute('SELECT * FROM applicability WHERE check_id=? ORDER BY rowid DESC LIMIT 1', (c['id'],)).fetchone()
                applicability = dict(review) if review else None
                if review:
                    applicability['current'] = not receipts and not attempts and review['basis'] == digest({'scope':scope.model_dump(mode='json'),'action':action.model_dump(mode='json')})
                    if applicability['current'] and review['decision'] == 'not_applicable':
                        state = State.NOT_APPLICABLE
                for o, r in zip(observations, receipts):
                    observation_rows.append({'id':o['id'],'artifact':o['artifact'],'tool':tools[o['artifact']],'receipt':r})
                checks.append({'id':c['id'], 'action':action.model_dump(), 'condition':CHECKS[action.check]['condition'], 'state':str(state), 'applicability':applicability, 'observations':[dict(o, receipt=json.loads(o['receipt'])) for o in observations], 'attempts':attempts})
            findings=correlate(observation_rows)
            by_id={o['id']:o for c in checks for o in c['observations']}
            for f in findings:
                for source in f['source_observations']:
                    source['freshness']=by_id[source['id']]['freshness']
                f['freshness_status']='all_evidence_stale' if all(s['freshness']['state'] in {'stale','future_timestamp'} for s in f['source_observations']) else 'inspect_source_times'
                f['evidence_digest'] = digest(sorted(f['evidence'], key=lambda e:e['observation']))
                risk=db.execute('SELECT * FROM risk_contexts WHERE assessment=? AND finding=? ORDER BY rowid DESC LIMIT 1',(assessment,f['id'])).fetchone()
                f['risk_context']=dict(risk,evidence_ids=json.loads(risk['evidence_ids'])) if risk else None
                f['risk_explanation']=explain_risk(f)
                latest = db.execute('SELECT * FROM reviews WHERE assessment=? AND finding=? ORDER BY rowid DESC LIMIT 1', (assessment, f['id'])).fetchone()
                f['review'] = dict(latest) if latest else None
                if latest:
                    f['status'] = latest['disposition'] if latest['evidence_digest'] == f['evidence_digest'] else 'review_outdated'
            ranked = sorted(findings, key=risk_key)
            snapshot = {'id':assessment, 'request':row['request'], 'created':row['created'], 'scope':scope.model_dump(), 'checks':checks, 'findings':ranked, 'unmatched':[dict(x, receipt=json.loads(x['receipt'])) for x in db.execute('SELECT * FROM unmatched WHERE assessment=? AND linked_check IS NULL ORDER BY created,id', (assessment,))], 'artifacts':[dict(x) for x in db.execute('SELECT id,tool,mode,sha256,created FROM artifacts WHERE assessment=?', (assessment,))], 'approvals':[dict(x) for x in db.execute('SELECT a.* FROM approvals a JOIN checks c ON c.id=a.check_id WHERE c.assessment=?', (assessment,))], 'events':[dict(x, payload=json.loads(x['payload'])) for x in db.execute('SELECT * FROM events WHERE assessment=? ORDER BY created,id', (assessment,))]}

            from .narrative import basis
            draft=next((e for e in reversed(snapshot['events']) if e['kind']=='report_drafted'),None)
            current=basis(snapshot)
            accepted=next((e for e in reversed(snapshot['events']) if e['kind']=='report_draft_accepted' and draft and e['payload']['draft_id']==draft['id'] and e['payload']['basis']==current),None)
            snapshot['report_draft']={'event':draft,'current':bool(draft and draft['payload']['basis']==current),'review':accepted} if draft else None
            return snapshot

    def set_applicability(self, check_id, decision, note, actor):
        if decision not in {'applicable', 'not_applicable'}:
            raise ValueError('Unknown applicability decision')
        if not 12 <= len(note.strip()) <= 2000 or not 1 <= len(actor.strip()) <= 200:
            raise ValueError('Analyst identity and a specific applicability reason are required')
        with self.tx() as db:
            c, scope, action = self.check_context(db, check_id)
            validate_scope(scope, action)
            evidence = db.execute('SELECT 1 FROM observations WHERE check_id=?', (check_id,)).fetchone()
            attempt = db.execute('SELECT 1 FROM attempts WHERE check_id=?', (check_id,)).fetchone()
            if evidence or attempt:
                raise ValueError('An applicability decision cannot replace observations or attempted-check outcomes')
            basis = action_fingerprint(scope, action)
            record = uid()
            db.execute('INSERT INTO applicability VALUES(?,?,?,?,?,?,?)', (record,check_id,decision,note.strip(),actor.strip(),basis,now()))
            self.event(db,c['assessment'],'applicability_reviewed',{'check':check_id,'decision':decision,'reason':note.strip(),'actor':actor.strip(),'basis':basis})
            return record

    def set_risk_context(self, assessment, finding, exposure, asset_impact, exploitability, evidence_ids, note, actor):
        if exposure not in {'unknown','lab_only','internal_per_owner','external_per_owner'} or asset_impact not in {'unknown','low','medium','high'} or exploitability not in {'not_assessed','analyst_validated'}:
            raise ValueError('Unsupported risk context value')
        if not 1<=len(actor.strip())<=200 or not 12<=len(note.strip())<=2000:
            raise ValueError('Provide analyst identity and a reason of 12-2000 characters')
        snap=self.snapshot(assessment)
        f=next((f for f in snap['findings'] if f['id']==finding),None)
        if f is None:raise KeyError('Finding not found in assessment')
        allowed={e['observation'] for e in f['evidence']}
        if not isinstance(evidence_ids,list) or not all(isinstance(x,str) for x in evidence_ids) or not set(evidence_ids)<=allowed:
            raise ValueError('Risk context must cite existing evidence from this finding')
        if exploitability=='analyst_validated' and not evidence_ids:
            raise ValueError('Analyst validation needs evidence references; a scanner title alone is insufficient')
        with self.tx() as db:
            id=uid()
            db.execute('INSERT INTO risk_contexts VALUES(?,?,?,?,?,?,?,?,?,?)',(id,assessment,finding,exposure,asset_impact,exploitability,json.dumps(evidence_ids),note.strip(),actor.strip(),now()))
            self.event(db,assessment,'risk_context_recorded',{'finding':finding,'exposure':exposure,'asset_impact':asset_impact,'exploitability':exploitability,'evidence_ids':evidence_ids,'note':note.strip(),'actor':actor.strip(),'limitation':'Analyst-declared context, not an independent verification or execution approval.'})
            return id

    def review_finding(self, assessment, finding, disposition, note, actor, evidence_digest):
        if disposition not in {'accepted_for_report', 'false_positive', 'needs_review'}:
            raise ValueError('Unknown finding review decision')
        if not 1 <= len(actor.strip()) <= 200 or not 12 <= len(note.strip()) <= 2000:
            raise ValueError('Provide analyst identity and a reason of 12-2000 characters')
        # Review is optimistic: later evidence automatically makes it outdated.
        snapshot = self.snapshot(assessment)
        selected = next((f for f in snapshot['findings'] if f['id'] == finding), None)
        if selected is None:
            raise KeyError('Finding not found in this assessment')
        if evidence_digest != selected['evidence_digest']:
            raise ValueError('Evidence changed; inspect the current finding before reviewing')
        with self.tx() as db:
            review = uid()
            db.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?,?,?)', (review,assessment,finding,disposition,note.strip(),actor.strip(),evidence_digest,now()))
            self.event(db, assessment, 'finding_reviewed', {'review':review,'finding':finding,'disposition':disposition,'note':note.strip(),'actor':actor.strip(),'evidence_digest':evidence_digest})
            return review

    def adopt_observation(self, assessment, observation):
        with self.tx() as db:
            _, scope = self.context(db, assessment)
            o = db.execute('SELECT * FROM unmatched WHERE id=? AND assessment=?', (observation,assessment)).fetchone()
            if o is None:
                raise KeyError('Unmatched observation not found')
            if o['linked_check']:
                return o['linked_check']
            r = Receipt.model_validate_json(o['receipt'])
            kind, *port = r.check.split(':')
            action = Action(check=kind,target=r.target,port=int(port[0]) if port else None,scope_revision=scope.revision)
            validate_scope(scope, action)
            existing = db.execute('SELECT id FROM checks WHERE assessment=? AND action=?', (assessment,action.model_dump_json())).fetchone()
            check = existing['id'] if existing else uid()
            if not existing:
                db.execute('INSERT INTO checks VALUES(?,?,?,?)', (check,assessment,action.model_dump_json(),now()))
            db.execute('INSERT INTO observations VALUES(?,?,?,?)', (o['id'],check,o['artifact'],o['receipt']))
            db.execute('UPDATE unmatched SET linked_check=? WHERE id=?', (check,observation))
            self.event(db, assessment, 'imported_observation_adopted', {'observation':observation,'check':check,'action':action.model_dump(),'note':'Analyst added an already-imported observation to the declared assessment plan; no scan executed.'})
            return check

    def save_decision(self, assessment, proposal):
        with self.tx() as db:
            self.event(db, assessment, 'planning_decision', proposal)

    def list_assessments(self):
        with self.tx() as db:
            return [dict(x) for x in db.execute('SELECT id,request,created FROM assessments ORDER BY created DESC')]
