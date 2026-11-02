from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import ipaddress
import json
from urllib.parse import urlsplit, urlunsplit
from pydantic import BaseModel, ConfigDict, Field, model_validator


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class State(StrEnum):
    UNATTEMPTED = 'unattempted'
    FINDING = 'finding_supported'
    NOT_OBSERVED = 'condition_not_observed'
    FAILED = 'failed'
    INCONCLUSIVE = 'inconclusive'
    CONFLICT = 'conflicting_observations'
    BLOCKED = 'blocked'
    NOT_APPLICABLE = 'not_applicable'
    STALE = 'stale_evidence'


class Scope(Strict):
    name: str = Field(min_length=1, max_length=200)
    revision: int = Field(default=1, ge=1)
    networks: tuple[str, ...]
    ports: tuple[int, ...] = Field(min_length=1)
    exclusions: tuple[str, ...] = ()
    authorization_reference: str = Field(min_length=8, max_length=1000)
    environment: str = 'self-owned-development'
    allowed_paths: tuple[str, ...] = ('/',)
    excluded_paths: tuple[str, ...] = ()
    evidence_max_age_hours: int = Field(default=24, ge=1, le=8760)

    @model_validator(mode='after')
    def validate_boundaries(self):
        if not self.networks or any(not 1 <= p <= 65535 for p in self.ports):
            raise ValueError('Explicit networks and valid ports required')
        for n in self.networks + self.exclusions:
            ipaddress.ip_network(n)
        if not self.allowed_paths:
            raise ValueError('Declare at least one allowed web path')
        for path in self.allowed_paths + self.excluded_paths:
            if not path.startswith('/') or any(x in path for x in ('%', '?', '#', '\\', '..')) or '//' in path or ';' in path or '.' in path.split('/') or any(c.isspace() for c in path):
                raise ValueError('Path boundaries must be unambiguous absolute paths')
        if self.environment not in {'self-owned-development', 'organizer-authorized'}:
            raise ValueError('Unknown authorization environment')
        return self


def canonical_target(target: str) -> tuple[str, str, int | None]:
    if len(target) > 2048 or any(c.isspace() for c in target):
        raise ValueError('Invalid target')
    if '://' not in target:
        addr = ipaddress.ip_address(target)
        return str(addr), str(addr), None
    u = urlsplit(target)
    if u.scheme not in ('http', 'https') or u.username or u.password or u.fragment:
        raise ValueError('Only HTTP(S), no credentials or fragments')
    addr = ipaddress.ip_address(u.hostname or '')  # literal IPs only: no DNS rebinding
    port = u.port or (443 if u.scheme == 'https' else 80)
    if not 1 <= port <= 65535 or '%' in u.path or '..' in u.path or '\\' in target or '//' in u.path or ';' in u.path or '.' in u.path.split('/'):
        raise ValueError('Ambiguous path/port unsupported')
    host = f'[{addr}]' if addr.version == 6 else str(addr)
    return urlunsplit((u.scheme, f'{host}:{port}', u.path or '/', u.query, '')), str(addr), port


CHECKS = {
    'tcp-port': {'tool': 'nmap', 'condition': 'TCP port is open', 'active': False},
    'web-server': {'tool': 'nikto', 'condition': 'Nikto reports a server issue at this endpoint', 'active': True},
    'web-alerts': {'tool': 'zap', 'condition': 'ZAP reports an alert at this endpoint', 'active': True},
    'header-nosniff': {'tool': 'http', 'condition': 'X-Content-Type-Options is absent or differs from nosniff', 'active': True},
}


class Action(Strict):
    check: str
    target: str
    port: int | None = None
    scope_revision: int = Field(ge=1)
    # No arbitrary options, shell, script or template identifiers accepted.

    @model_validator(mode='after')
    def registered(self):
        if self.check not in CHECKS:
            raise ValueError('Unknown registered check')
        canonical_target(self.target)
        if self.check == 'tcp-port':
            if '://' in self.target or self.port is None or not 1 <= self.port <= 65535:
                raise ValueError('TCP check requires literal IP and port')
        elif '://' not in self.target or self.port is not None:
            raise ValueError('Web check requires exact URL without separate port')
        return self


def validate_scope(scope: Scope, action: Action):
    _, host, urlport = canonical_target(action.target)
    addr = ipaddress.ip_address(host)
    if action.scope_revision != scope.revision:
        raise ValueError('Scope revision changed; new plan and approval required')
    if not any(addr in ipaddress.ip_network(n) for n in scope.networks):
        raise ValueError('Target outside approved networks')
    if any(addr in ipaddress.ip_network(n) for n in scope.exclusions):
        raise ValueError('Target explicitly excluded')
    if (action.port or urlport) not in scope.ports:
        raise ValueError('Port outside approved scope')
    if urlport is not None:
        path = urlsplit(canonical_target(action.target)[0]).path
        def within(boundary):
            return boundary == '/' or path == boundary.rstrip('/') or path.startswith(boundary.rstrip('/') + '/')
        if not any(within(p) for p in scope.allowed_paths):
            raise ValueError('Path outside approved web boundaries')
        if any(within(p) for p in scope.excluded_paths):
            raise ValueError('Path explicitly excluded')


def action_fingerprint(scope: Scope, action: Action):
    validate_scope(scope, action)
    return digest({'scope': scope.model_dump(mode='json'), 'action': action.model_dump(mode='json')})


class Receipt(Strict):
    target: str
    check: str
    outcome: State
    detail: str
    source_ref: str
    issue_class: str | None = None
    title: str | None = None
    severity: str = 'unknown'
    confidence: str = 'tool-reported'
    observed_at: str | None = None
    remediation: str | None = None


def coverage(receipts: list[Receipt], *, stale=False, blocked=False):
    if stale and receipts:
        return State.STALE
    outcomes = {r.outcome for r in receipts}
    if State.CONFLICT in outcomes or {State.FINDING, State.NOT_OBSERVED} <= outcomes:
        return State.CONFLICT
    if State.FINDING in outcomes:
        return State.FINDING
    if State.FAILED in outcomes:
        return State.FAILED
    if State.NOT_OBSERVED in outcomes:
        return State.NOT_OBSERVED
    if State.INCONCLUSIVE in outcomes:
        return State.INCONCLUSIVE
    if State.NOT_APPLICABLE in outcomes:
        return State.NOT_APPLICABLE
    return State.BLOCKED if blocked else State.UNATTEMPTED
