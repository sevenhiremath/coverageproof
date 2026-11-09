from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import pytest
from pypdf import PdfReader
from coverageproof.domain import Action, Receipt, State, now
from coverageproof.recovery import main
from coverageproof.report import generate


def interrupted(store, scope):
    assessment = store.create('Recover an interrupted owned check', scope)
    check = store.add_check(assessment, Action(check='header-nosniff', target='http://127.0.0.1:8765/', scope_revision=1))
    approval = store.approve(check, 'Unit analyst')
    attempt, _, _ = store.claim(check, approval)
    return assessment, check, approval, attempt


def age_attempt(store, attempt):
    old = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    with store.tx() as db:
        db.execute('UPDATE attempts SET created=? WHERE id=?', (old, attempt))


def test_recovery_keeps_failed_state_and_consumed_approval(store, scope):
    a, check, approval, attempt = interrupted(store, scope)
    age_attempt(store, attempt)
    store.recover_attempt(attempt, 'Unit analyst', 'App process was stopped after a simulated crash', workers_stopped=True)
    snap = store.snapshot(a)
    assert snap['checks'][0]['state'] == 'failed'
    assert snap['coverage_summary']['unanswered_total'] == 1
    assert not snap['artifacts'] and not snap['findings']
    event = next(e for e in snap['events'] if e['kind'] == 'execution_recovered')
    assert event['payload']['actor'] == 'Unit analyst'
    with pytest.raises(ValueError, match='consumed'):
        store.claim(check, approval)
    # A late worker cannot append a fabricated success after recovery.
    with pytest.raises(ValueError, match='not running'):
        store.finish(attempt, 'completed', 'Late result', b'late synthetic receipt', Receipt(
            target='http://127.0.0.1:8765/', check='header-nosniff', outcome=State.NOT_OBSERVED,
            detail='Synthetic late receipt', source_ref='unit', observed_at=now()))
    text = ' '.join(' '.join(p.extract_text() for p in PdfReader(BytesIO(generate(store, a))).pages).split())
    assert 'execution_recovered' in text and 'no completed result is inferred' in text
    fresh = store.approve(check, 'Unit analyst')
    new_attempt, _, _ = store.claim(check, fresh)
    assert new_attempt != attempt


def test_recovery_rejects_live_recent_or_unattributed_changes(store, scope):
    _, _, _, attempt = interrupted(store, scope)
    with pytest.raises(ValueError, match='workers_stopped'):
        store.recover_attempt(attempt, 'Unit analyst', 'Reason for closing an interrupted action')
    with pytest.raises(ValueError, match='60 seconds'):
        store.recover_attempt(attempt, 'Unit analyst', 'Stopped process but this record is too recent', workers_stopped=True)
    age_attempt(store, attempt)
    with pytest.raises(ValueError, match='identity'):
        store.recover_attempt(attempt, ' ', 'Reason for closing an interrupted action', workers_stopped=True)
    with store.tx() as db:
        assert db.execute('SELECT status FROM attempts WHERE id=?', (attempt,)).fetchone()['status'] == 'running'


def test_concurrent_recovery_records_only_one_transition(store, scope):
    a, _, _, attempt = interrupted(store, scope)
    age_attempt(store, attempt)
    def recover(_):
        try:
            store.recover_attempt(attempt, 'Unit analyst', 'Stopped all processes before this recovery', workers_stopped=True)
            return 'recovered'
        except ValueError:
            return 'rejected'
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(recover, range(2))) == ['recovered', 'rejected']
    assert sum(e['kind'] == 'execution_recovered' for e in store.snapshot(a)['events']) == 1


def test_recovery_cli_lists_and_requires_stop_attestation(store, scope, capsys, tmp_path):
    _, _, _, attempt = interrupted(store, scope)
    main(['--db', store.path, '--list'])
    assert json.loads(capsys.readouterr().out)[0]['id'] == attempt
    with pytest.raises(SystemExit):
        main(['--db', store.path, '--attempt', attempt])
    missing = tmp_path / 'wrong-path.sqlite'
    with pytest.raises(SystemExit):
        main(['--db', str(missing), '--list'])
    assert not missing.exists()
    age_attempt(store, attempt)
    main(['--db', store.path, '--attempt', attempt, '--workers-stopped', '--actor', 'Unit analyst',
          '--reason', 'Stopped all processes before this recovery'])
    assert 'No action ran' in capsys.readouterr().out
