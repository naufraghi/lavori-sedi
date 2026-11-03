from ._anvil_designer import EditEventTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from datetime import datetime, time, timedelta

class EditEvent(EditEventTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.event_id = properties.get("event_id")
    self.item = properties.get("item")
    self.is_new = self.event_id is None
    self.location = properties.get("location")
    self.admin = properties.get("admin", False)
    self.past_events = properties.get("past_events", False)

    locations = anvil.server.call("get_event_locations")
    self.location_picker.items = locations
    self.location_picker.selected_value = self.item["location"] if self.item else None
    self.use_new_location = False
    self.new_location_text.visible = False
    self.existing_location_button.visible = False

    if self.item:
      self.event_title.text = self.item["title"]
      self.event_date.date = self.item["start_datetime"].date()
      self.event_start.selected_value = self.item["start_datetime"].strftime('%H:%M')
      duration = self.item["end_datetime"] - self.item["start_datetime"]
      self.event_duration.selected_value = f"{int(duration.total_seconds()/(60*60))}h"
      self.event_description.text = self.item["description"] or ""
      self.event_hidden.checked = self.item["hidden"]
    else:
      self.event_title.text = ""
      self.event_date.date = None
      self.event_start.selected_value = "09:00"
      self.event_duration.selected_value = "2h"
      self.event_description.text = ""
      self.event_hidden.checked = False

    self.manager_dropdown.items = [(m['name'], m) for m in (anvil.server.call('get_managers') or [])]
    self.manager_dropdown.selected_value = self.item['manager'] if self.item else None
    self.duplica_button.visible = not self.is_new
    self.save_button.text = "Crea evento" if self.is_new else "Salva"

  def new_location_click(self, **event_args):
    self.use_new_location = True
    self.location_picker.visible = False
    self.new_location_button.visible = False
    self.new_location_text.visible = True
    self.existing_location_button.visible = True

  def existing_location_click(self, **event_args):
    self.use_new_location = False
    self.new_location_text.text = ""
    self.new_location_text.visible = False
    self.existing_location_button.visible = False
    self.location_picker.visible = True
    self.new_location_button.visible = True

  def save_button_click(self, **event_args):
    event_date = self.event_date.date
    if event_date is None:
      alert("Seleziona una data per l'evento.")
      return

    title = (self.event_title.text or "").strip()
    if not title:
      alert("Inserisci il titolo dell'evento.")
      return

    if self.use_new_location:
      location = (self.new_location_text.text or "").strip()
    else:
      location = self.location_picker.selected_value
    if not location:
      alert("Scegli una sede o inseriscine una nuova.")
      return

    if not self.event_start.selected_value or not self.event_duration.selected_value:
      alert("Seleziona l'orario e la durata dell'evento.")
      return

    new_values = {}
    new_values["title"] = title
    new_values["description"] = self.event_description.text
    hour, minute = map(int, self.event_start.selected_value.split(":"))
    start_datetime = datetime.combine(event_date, time(hour, minute))
    duration = int(self.event_duration.selected_value.strip("h"))
    new_values["start_datetime"] = start_datetime
    new_values["end_datetime"] = start_datetime + timedelta(hours=duration)
    new_values["location"] = location
    new_values["manager"] = self.manager_dropdown.selected_value
    new_values["hidden"] = self.event_hidden.checked

    if self.is_new:
      result = anvil.server.call("create_event", **new_values)
      if not result["ok"]:
        alert(result["message"])
        return
    else:
      anvil.server.call("set_event", self.event_id, **new_values)
    open_form("EventsForm", location=self.location, admin=self.admin,
              past_events=self.past_events)

  def duplica_button_click(self, **event_args):
    new_event = anvil.server.call('duplicate_event', self.event_id)
    open_form("EditEvent", event_id=new_event.get_id(), item=new_event,
              location=self.location, admin=self.admin,
              past_events=self.past_events)
  
  def indietro_button_click(self, **event_args):
    """This method is called when the component is clicked."""
    open_form("EventsForm", location=self.location, admin=self.admin,
              past_events=self.past_events)
