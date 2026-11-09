"""Inspect interrupted jobs or close one after stopping all app workers."""
import argparse
import json
from pathlib import Path
from .store import Store


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, help='Existing CoverageProof database')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--list', action='store_true', help='List running records without changing them')
    action.add_argument('--attempt', help='Exact attempt ID to mark failed without retrying')
    parser.add_argument('--workers-stopped', action='store_true', help='Attest every app/runner using this database is stopped')
    parser.add_argument('--actor')
    parser.add_argument('--reason')
    args = parser.parse_args(argv)
    if not Path(args.db).is_file():
        parser.error('Database must already exist; check the path')
    # Listing is read-only and does not initialize/migrate a database.
    if args.list:
        import sqlite3
        uri = Path(args.db).resolve().as_uri() + '?mode=ro'
        with sqlite3.connect(uri, uri=True) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT id,check_id,created,status FROM attempts WHERE status='running' ORDER BY created,id").fetchall()
        print(json.dumps([dict(row) for row in rows], indent=2))
        return
    if not args.workers_stopped or not args.actor or not args.reason:
        parser.error('Recovery requires --workers-stopped, --actor and --reason; stop every worker first')
    try:
        Store(args.db).recover_attempt(args.attempt, args.actor, args.reason, workers_stopped=True)
    except (ValueError, KeyError) as error:
        parser.error(str(error))
    print('Interrupted attempt marked failed. No action ran. A retry requires a fresh approval.')


if __name__ == '__main__':
    main()
