"""Collection time is separate from import time; unknown times stay unknown."""
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime


def collection_time(value):
    if value is None:return None
    try:
        value=str(value).strip()
        if value.isdigit():return datetime.fromtimestamp(int(value),tz=timezone.utc)
        try:t=datetime.fromisoformat(value.replace('Z','+00:00'))
        except ValueError:
            try:t=datetime.strptime(value,'%Y-%m-%d %H:%M:%S %z')
            except ValueError:t=parsedate_to_datetime(value)
        if t.tzinfo is None:return None
        return t.astimezone(timezone.utc)
    except (ValueError,TypeError,OverflowError,OSError):return None


def freshness(value, max_age_hours, *, reference=None):
    reference=reference or datetime.now(timezone.utc)
    collected=collection_time(value)
    if collected is None:return {'state':'unknown','collected_at':None,'reason':'Native output supplied no supported timestamp with a timezone.'}
    if collected>reference+timedelta(minutes=5):return {'state':'future_timestamp','collected_at':collected.isoformat(),'reason':'Collection time is ahead of the current clock; check source time and timezone.'}
    if reference-collected>timedelta(hours=max_age_hours):return {'state':'stale','collected_at':collected.isoformat(),'reason':f'Collection is older than the declared {max_age_hours}-hour evidence window.'}
    return {'state':'current_window','collected_at':collected.isoformat(),'reason':f'Within the declared {max_age_hours}-hour evidence window; this does not authenticate the import.'}
