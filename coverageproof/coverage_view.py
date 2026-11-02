"""Present the saved coverage states; no UI or model text changes their meaning."""
from collections import Counter
from .domain import State

REASONS={
    State.UNATTEMPTED:'No matching observation or execution attempt exists for this declared check.',
    State.FAILED:'An attempted check failed; the intended condition remains unanswered.',
    State.INCONCLUSIVE:'The available output is insufficient to answer this declared condition.',
    State.CONFLICT:'Stored observations disagree; inspect their source, time and configuration.',
    State.STALE:'Evidence or scope revision is stale; a current answer is not established.',
    State.BLOCKED:'Scope or approval policy prevents this action; no result is inferred.',
    State.NOT_APPLICABLE:'An attributed applicability review excludes this unattempted check.',
    State.NOT_OBSERVED:'This declared condition was not observed in the interpretable receipt; other conditions remain unknown.',
    State.FINDING:'Evidence supports this declared condition; service discovery alone is not a vulnerability.',
}
ANSWERED={State.FINDING,State.NOT_OBSERVED}


def summarize(checks):
    counts=Counter(c['state'] for c in checks)
    gaps=[{'check_id':c['id'],'target':c['action']['target'],'port':c['action']['port'],
        'condition':c['condition'],'state':c['state'],'reason':REASONS[State(c['state'])]} for c in checks if c['state'] not in ANSWERED|{State.NOT_APPLICABLE}]
    return {'declared_total':len(checks),'answered_total':sum(counts[s] for s in ANSWERED),
        'not_applicable_total':counts[State.NOT_APPLICABLE],'unanswered_total':len(gaps),'state_counts':dict(counts),'gaps':gaps}
