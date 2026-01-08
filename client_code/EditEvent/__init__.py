from ._anvil_designer import EditEventTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from datetime import datetime, time

class EditEvent(EditEventTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.event_id = properties.get("event_id")
    self.event_title.text = self.item["title"]
    self.event_date.date = self.item["start_datetime"].date()
    self.event_start.selected_value = self.item["start_datetime"].strftime('%H:%M')
    duration = self.item["end_datetime"] - self.item["start_datetime"]
    self.event_duration.selected_value = f"{int(duration.total_seconds()/(60*60))}h"
    self.event_description.text = self.item["description"]
    self.event_hidden.checked = self.item["hidden"]
    self.manager_dropdown.items = [(m['name'], m) for m in (anvil.server.call('get_managers') or [])]
    self.manager_dropdown.selected_value = self.item['manager'] #['name'] if self.item['manager'] else None

  def save_button_click(self, **event_args):
    new_values = {}
    new_values["title"] = self.event_title.text
    new_values["description"] = self.event_description.text
    hour, minute = map(int, self.event_start.selected_value.split(":"))
    new_values["start_datetime"] = datetime.combine(self.event_date.date, time(hour, minute))
    duration = int(self.event_duration.selected_value.strip("h"))
    new_values["end_datetime"] = datetime.combine(self.event_date.date, time(hour+duration, minute))
    new_values["manager"] = self.manager_dropdown.selected_value
    new_values["hidden"] = self.event_hidden.checked
    anvil.server.call("set_event", self.event_id, **new_values)
    open_form("EventsForm")

  def duplica_button_click(self, **event_args):
    new_event = anvil.server.call('duplicate_event', self.event_id)
    open_form("EditEvent", event_id=new_event.get_id(), item=new_event)
  
  def indietro_button_click(self, **event_args):
    """This method is called when the component is clicked."""
    open_form("EventsForm")
