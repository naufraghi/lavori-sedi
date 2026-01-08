from ._anvil_designer import EventsFormTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class EventsForm(EventsFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.admin = properties.get('admin', False)
    self.load_events()

  def load_events(self):
      if self.admin:
        events = anvil.server.call('get_all_events')
      else:
        events = anvil.server.call('get_upcoming_events')
      self.events_list.items = events

  @handle("link_1", "click")
  def link_1_click(self, **event_args):
    """This method is called clicked"""
    self.admin = True
    self.load_events()
