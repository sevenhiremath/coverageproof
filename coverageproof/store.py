from __future__ import annotations
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from .adapters import parse
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
CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),finding TEXT NOT NULL,disposition TEXT NOT NULL,note TEXT NOT NULL,actor TEXT NOT NULL,evidence_digest TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS unmatched(id TEXT PRIMARY KEY,assessment TEXT REFERENCES assessments(id),artifact TEXT REFERENCES artifacts(id),receipt TEXT NOT NULL,created TEXT NOT NULL,linked_check TEXT REFERENCES checks(id));
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
            fp = action_fingerprint(scope, action)
            approved = db.execute('SELECT * FROM approvals WHERE id=? AND check_id=? AND fingerprint=? AND consumed IS NULL', (approval, check_id, fp)).fetchone()
            active = db.execute("SELECT 1 FROM attempts WHERE status='running'").fetchone()
            reason = 'Approval missing, consumed or bound to another action' if approved is None else 'Runner concurrency limit (one job) reached' if active else None
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
            checks, findings = [], {}
            for c in db.execute('SELECT * FROM checks WHERE assessment=? ORDER BY created,id', (assessment,)).fetchall():
                action = Action.model_validate_json(c['action'])
                observations = [dict(x) for x in db.execute('SELECT * FROM observations WHERE check_id=?', (c['id'],))]
                receipts = [Receipt.model_validate_json(o['receipt']) for o in observations]
                attempts = [dict(x) for x in db.execute('SELECT * FROM attempts WHERE check_id=?', (c['id'],))]
                state = coverage(receipts, stale=action.scope_revision != scope.revision)
                if attempts and state == State.UNATTEMPTED:
                    state = State.FAILED if attempts[-1]['status'] in {'failed','timeout','unsupported'} else State.INCONCLUSIVE
                for o, r in zip(observations, receipts):
                    if r.issue_class:
                        key = (canonical_target(r.target)[0], r.issue_class)
                        f = findings.setdefault(key, {'id':sha256(repr(key).encode()).hexdigest()[:12], 'asset':key[0], 'issue_class':r.issue_class, 'title':r.title, 'severity':r.severity, 'confidence':r.confidence, 'status':'suspected; analyst review required', 'evidence':[], 'remediation':r.remediation or 'Review the source evidence and confirm applicability before selecting remediation.', 'impact':'Not independently established; depends on affected asset and validation.', 'cvss':None})
                        f['evidence'].append({'observation':o['id'], 'artifact':o['artifact'], 'source_ref':r.source_ref})
                checks.append({'id':c['id'], 'action':action.model_dump(), 'condition':CHECKS[action.check]['condition'], 'state':str(state), 'observations':[dict(o, receipt=json.loads(o['receipt'])) for o in observations], 'attempts':attempts})
            for f in findings.values():
                f['evidence_digest'] = digest(sorted(f['evidence'], key=lambda e:e['observation']))
                latest = db.execute('SELECT * FROM reviews WHERE assessment=? AND finding=? ORDER BY rowid DESC LIMIT 1', (assessment, f['id'])).fetchone()
                f['review'] = dict(latest) if latest else None
                if latest:
                    f['status'] = latest['disposition'] if latest['evidence_digest'] == f['evidence_digest'] else 'review_outdated'
            ranked = sorted(findings.values(), key=lambda f: ({'critical':0,'high':1,'medium':2,'low':3,'informational':4,'unknown':5}[f['severity']], f['asset'], f['id']))
            return {'id':assessment, 'request':row['request'], 'created':row['created'], 'scope':scope.model_dump(), 'checks':checks, 'findings':ranked, 'unmatched':[dict(x, receipt=json.loads(x['receipt'])) for x in db.execute('SELECT * FROM unmatched WHERE assessment=? AND linked_check IS NULL ORDER BY created,id', (assessment,))], 'artifacts':[dict(x) for x in db.execute('SELECT id,tool,mode,sha256,created FROM artifacts WHERE assessment=?', (assessment,))], 'approvals':[dict(x) for x in db.execute('SELECT a.* FROM approvals a JOIN checks c ON c.id=a.check_id WHERE c.assessment=?', (assessment,))], 'events':[dict(x, payload=json.loads(x['payload'])) for x in db.execute('SELECT * FROM events WHERE assessment=? ORDER BY created,id', (assessment,))]}

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
