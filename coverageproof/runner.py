"""Restricted in-process boundary for a single bounded HTTP check.

Scanner CLIs intentionally disabled until an isolated egress-limited runner exists.
Literal IPs avoid DNS. Redirects and environment proxies are disabled.
"""
import httpx
import time
from .domain import Receipt, State, canonical_target, now, validate_scope

LIMIT = 131072


def execute(store, check_id, approval):
    attempt, scope, action = store.claim(check_id, approval)
    try:
        validate_scope(scope, action)  # runner revalidation
        if action.check != 'header-nosniff':
            store.finish(attempt, 'unsupported', 'Native scanner live execution unavailable; import genuine native output instead.')
            return
        target = canonical_target(action.target)[0]
        with httpx.Client(trust_env=False, follow_redirects=False, timeout=httpx.Timeout(5), limits=httpx.Limits(max_connections=1)) as client:
            deadline = time.monotonic() + 10
            with client.stream('GET', target, headers={'User-Agent':'CoverageProof/0.1 authorized-check'}) as response:
                raw = (f'HTTP {response.status_code}\n' + '\n'.join(f'{k}: {v}' for k,v in response.headers.multi_items()) + '\n\n').encode()
                for chunk in response.iter_raw():
                    if time.monotonic() > deadline:
                        raise httpx.ReadTimeout("Overall request deadline exceeded")
                    raw += chunk
                    if len(raw) > LIMIT:
                        raise ValueError('Response output limit exceeded')
                interpretable = 200 <= response.status_code < 300
                present = response.headers.get('x-content-type-options', '').lower().strip() == 'nosniff'
                outcome = (State.NOT_OBSERVED if present else State.FINDING) if interpretable else State.INCONCLUSIVE
                receipt = Receipt(target=target, check=action.check, outcome=outcome,
                    issue_class='header:x-content-type-options' if interpretable and not present else None,
                    title='Missing or unexpected X-Content-Type-Options' if interpretable and not present else None,
                    severity='low' if interpretable and not present else 'unknown',
                    detail=f'GET {target}; HTTP {response.status_code}; nosniff={present}. Only this response and condition assessed; redirects not followed.',
                    source_ref='HTTP response headers', observed_at=now(), confidence='direct response observation',
                    remediation='Set X-Content-Type-Options: nosniff on the affected response and verify content types.')
                store.finish(attempt, 'completed', 'One response recorded; no broader security conclusion.', raw, receipt)
    except httpx.TimeoutException:
        store.finish(attempt, 'timeout', 'HTTP timeout; target reach and condition remain unknown.')
    except Exception as e:
        store.finish(attempt, 'failed', f'{type(e).__name__}: {e}')
