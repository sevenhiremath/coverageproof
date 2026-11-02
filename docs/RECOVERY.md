# Recover an interrupted check

A stopped process can leave its last attempt marked `running`. The one-job rule then blocks new executions. This command closes that database record as failed; it does not stop a process, recover an unseen response, restore approval or rerun a check.

1. Stop every app and runner using this database, including other terminals, reload processes and containers. The operator must verify this: the command cannot prove it.
2. Inspect the running records without changing them:

```bash
python -m coverageproof.recovery --db data/coverageproof.sqlite --list
```

3. Wait until the selected record is at least 60 seconds old. Use its exact attempt ID and record who checked that the processes stopped:

```bash
python -m coverageproof.recovery --db data/coverageproof.sqlite --attempt ATTEMPT_ID --workers-stopped --actor 'Local analyst' --reason 'Stopped the app after it exited during the owned HTTP check'
```

4. Restart the app. The check stays unanswered with a failed attempt. Inspect its recorded reason and source evidence. If a retry is appropriate, create a fresh approval for the exact action.

The path must exist; a typo does not create an empty replacement database. Use the Python interpreter where CoverageProof is installed. Do not run recovery while an old worker may still be making a request. The age check is only an extra guard against mistakes, not a process-liveness check. A dishonest or mistaken stop attestation can still permit overlapping network work. This tool remains a single-operator local app.

| Choice | Benefit | Alternative and why we skipped it | Drawback | Verification |
|---|---|---|---|---|
| Explicit offline recovery of one attempt | Operator chooses the exact interrupted record and records a reason | Reset every running record at startup: another app process could still own it | Requires stopping all workers manually | Missing stop attestation, recent attempts and missing identity are rejected |
| Mark failed and keep the approval consumed | No invisible success or automatic repeat after a crash | Restore approval or auto-retry: request may already have reached the target | Requires another approval and does not recover lost responses | Old approval reuse fails; new approval can claim a new attempt |
| Same SQLite transaction for transition and audit | Two recovery calls cannot both record a successful transition | Edit the database directly: easy to lose audit history | SQLite still serializes writers | Concurrent recovery produces one transition; late finish cannot add evidence |
| No new scheduler or worker dependency | Small enough to inspect and explain | Worker leases/heartbeats: useful for multiple workers but more moving parts here | Manual intervention, no automatic distributed recovery | End-to-end CLI and report tests preserve failure/unknown wording |

The minimum age is chosen above the HTTP runner's normal deadlines. It does not authorize new native scanner runners; adding those would require revisiting recovery and their cancellation behavior. The recovery event appears in the assessment audit and subsequent PDF snapshots. Existing immutable reports remain historical records.
