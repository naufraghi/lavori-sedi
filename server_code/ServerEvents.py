import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.tz

from datetime import datetime

@anvil.server.callable
def get_upcoming_events():
    now = datetime.now(anvil.tz.tzlocal())
    kwargs = {"end_datetime": q.greater_than(now)}
    if not is_clan():
      kwargs['hidden'] = False
    events = app_tables.events.search(tables.order_by("start_datetime"), **kwargs)
    return [dict(
        id=e.get_id(),
        title=e['title'],
        start=e['start_datetime'],
        end=e['end_datetime'],
        location=e['location'],
        description=e['description'],
        participants=e['participants'] or [],
        manager=e['manager'],
        hidden=e['hidden'],
    ) for e in events]

@anvil.server.callable
def get_event(event_id):
    return app_tables.events.get_by_id(event_id)

@anvil.server.callable
def set_event(event_id, **new_values):
    event = app_tables.events.get_by_id(event_id)
    manager_name = new_values.pop("manager_name", None)
    manager = app_tables.participants.get(name=manager_name, manager=True)
    event['manager'] = manager
    for key in new_values:
      event[key] = new_values[key]

@anvil.server.callable
def duplicate_event(event_id):
  event = app_tables.events.get_by_id(event_id)
  new_event = app_tables.events.add_row(**dict(event))
  new_event['title'] = new_event['title'] + " (copia)"
  new_event['hidden'] = True
  new_event['participants'] = []
  return new_event

@anvil.server.callable
def get_managers():
  return app_tables.participants.search(manager=True)

@anvil.server.callable
def sign_up(event_id, name, email, role):
    event = app_tables.events.get_by_id(event_id)
    if not event:
        raise Exception("Event not found")
    anvil.server.cookies.local["name"] = name
    anvil.server.cookies.local["email"] = email
    anvil.server.cookies.local["role"] = role
    part = app_tables.participants.get(name=name, email=email, role=role)
    if part is None:
      part = app_tables.participants.add_row(name=name, email=email, role=role)
    participants = event["participants"] if event["participants"] else []
    if part not in participants:
      event["participants"] = participants+[part]

@anvil.server.callable
def is_signed_up(event_id, name, email, role):
    event = app_tables.events.get_by_id(event_id)
    if not event:
        raise Exception("Event not found")
    participants = event["participants"] if event["participants"] else []
    return app_tables.participants.get(name=name, email=email, role=role) in participants

@anvil.server.callable
def sign_out(event_id, name, email, role):
    event = app_tables.events.get_by_id(event_id)
    if not event:
        raise Exception("Event not found")
    part = app_tables.participants.get(name=name, email=email, role=role)
    if part is None:
      return False
    participants = event["participants"] if event["participants"] else []
    if part in participants:
      event["participants"] = [p for p in participants if (p != part)]

@anvil.server.callable
def load_defaults():
  name = anvil.server.cookies.local.get("name", "")
  email = anvil.server.cookies.local.get("email", "")
  role = anvil.server.cookies.local.get("role", "genitore")
  return {"name": name, "email": email, "role": role}

@anvil.server.callable
def is_clan():
  return anvil.server.cookies.local.get("role", "genitore") == "clan"

@anvil.server.route("/admin-events")
def admin_events(**p):
  return anvil.server.FormResponse('EventsForm', admin=True)