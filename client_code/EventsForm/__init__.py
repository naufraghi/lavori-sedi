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
    self.load_events()

  def load_events(self):
      events = anvil.server.call('get_upcoming_events')
      self.events_list.items = events
