import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime

@anvil.server.callable
def get_upcoming_events():
    now = datetime.now()
    events = app_tables.events.search(start_time__gte=now, archived=False, sort=True)
    return [dict(
        id=e.get_id(),
        title=e['title'],
        start=e['start_datetime'],
        end=e['end_datetime'],
        location=e['location'],
        description=e['description'],
        participants=[p['name'] for p in e['participants'].search()]
    ) for e in events]

@anvil.server.callable
def sign_up(event_id, name, email):
    event = app_tables.events.get_by_id(event_id)
    if not event:
        raise Exception("Event not found")
    app_tables.participants.add_row(name=name, email=email, event=event)