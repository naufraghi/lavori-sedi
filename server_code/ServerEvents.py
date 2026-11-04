import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.tz

from datetime import datetime, timedelta

@anvil.server.callable
def get_event_locations():
  locations = set()
  for event in app_tables.events.search():
    location = event["location"]
    if location:
      location = location.strip()
      if location:
        locations.add(location)

  canonical_locations = {}
  for location in sorted(locations, key=lambda value: (value.casefold(), value)):
    canonical_locations.setdefault(location.casefold(), location)
  return list(canonical_locations.values())

@anvil.server.callable
def get_upcoming_events():
    now = datetime.now(anvil.tz.tzlocal())
    cutoff = now - timedelta(hours=24)
    kwargs = {
      "end_datetime": q.greater_than(cutoff),
      "hidden": False,
    }
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
        modify=False
    ) for e in events]

@anvil.server.callable
def get_all_events(past_events=None):
  events = app_tables.events.search(tables.order_by("start_datetime"))
  if past_events is not None:
    cutoff = datetime.now(anvil.tz.tzlocal()) - timedelta(hours=24)
    if past_events:
      events = [e for e in events
                if e['end_datetime'] is not None and e['end_datetime'] <= cutoff]
    else:
      events = [e for e in events
                if e['end_datetime'] is not None and e['end_datetime'] > cutoff]
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
    modify=True,
  ) for e in events]

@anvil.server.callable
def get_event(event_id):
    return app_tables.events.get_by_id(event_id)

@anvil.server.callable
def set_event(event_id, **new_values):
    event = app_tables.events.get_by_id(event_id)
    for key in new_values:
      event[key] = new_values[key]

@anvil.server.callable
def create_event(title, start_datetime, end_datetime, description, location,
                 manager=None, hidden=False):
  title = (title or "").strip()
  location = (location or "").strip()
  if not title:
    return {"ok": False, "message": "Inserisci il titolo dell'evento."}
  if not location:
    return {"ok": False, "message": "Scegli o inserisci una sede."}
  if end_datetime <= start_datetime:
    return {"ok": False, "message": "La fine dell'evento deve essere successiva all'inizio."}

  for existing_location in get_event_locations():
    if existing_location.casefold() == location.casefold():
      location = existing_location
      break

  if manager is not None:
    manager = app_tables.participants.get_by_id(manager.get_id())
    if manager is None or not manager["manager"]:
      return {"ok": False, "message": "Seleziona un referente valido."}

  app_tables.events.add_row(
    title=title,
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    description=description or "",
    location=location,
    manager=manager,
    hidden=bool(hidden),
  )
  return {"ok": True}

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
