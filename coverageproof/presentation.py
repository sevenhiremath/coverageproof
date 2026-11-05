"""Operational facts derived from registered actions and current scope."""
from urllib.parse import urlsplit
from .domain import Action, Scope, validate_scope


def action_facts(action, scope):
    try:
        action=Action.model_validate(action)
        validate_scope(Scope.model_validate(scope),action)
        verdict='Allowed by current scope; execution approval is separate.'
    except ValueError:
        verdict='Current scope validation failed; review scope and action before proceeding.'
    if isinstance(action,Action) and action.check=='header-nosniff':
        operation='Execute one HTTP GET after exact one-use approval.'
        limit='One response and one header condition at the exact URL. Other routes, response variants and vulnerability classes remain unassessed.'
    else:
        operation='Review an imported scanner export. Scanner execution is disabled in this app.'
        limit='Coverage depends on the imported export and its configuration. Missing findings do not prove that a condition was tested or absent.'
    return dict(scope=verdict,operation=operation,limit=limit)


def applicability_note(finding):
    sources=finding.get('source_observations',[])
    if urlsplit(finding['asset']).scheme=='http' and any(
            'strict-transport-security' in s.get('detail','').lower() for s in sources):
        return ('HSTS applicability review: this source claim concerns a plain HTTP URL. '
                'HSTS is enforced through HTTPS responses; this HTTP observation alone '
                'does not establish whether the HTTPS endpoint has a valid HSTS policy or an exploitable weakness.')
    return None
