from ._anvil_designer import EventsFormTemplate
from anvil import *
import anvil.server
from m3.components import Button as M3Button


class EventsForm(EventsFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.admin = properties.get('admin', False)
    self.requested_location = properties.get('location')
    self.selected_location = self.requested_location
    self.past_events = properties.get('past_events', False)
    self.filter_panel.visible = self.admin
    self.location_filter_panel.visible = True
    self.recent_events_button.visible = self.admin
    self.past_events_button.visible = self.admin
    self.new_event_button.visible = self.admin
    self.location_filter_buttons = []
    self.update_admin_filter_buttons()
    self.load_events()

  def load_events(self):
    self.locations = anvil.server.call('get_event_locations')

    if self.admin:
      self.all_events = anvil.server.call('get_all_events', self.past_events)
      for event in self.all_events:
        event['past_events'] = self.past_events
    else:
      self.all_events = anvil.server.call('get_upcoming_events')

    self.location_filter_panel.clear()
    self.location_filter_buttons = []
    self.add_location_filter_button('Tutte le sedi', None)
    for location in self.locations:
      self.add_location_filter_button(location, location)

    if self.selected_location not in self.locations:
      self.selected_location = None

    self.show_location(self.selected_location)

  def add_location_filter_button(self, label, location):
    button = M3Button(text=label, appearance='outlined')
    button.set_event_handler('click', self.make_location_filter_handler(location))
    self.location_filter_panel.add_component(button)
    self.location_filter_buttons.append((location, button))

  def make_location_filter_handler(self, location):
    def handler(**event_args):
      self.show_location(location)
    return handler

  def update_location_filter_buttons(self, selected_location):
    for location, button in self.location_filter_buttons:
      if location is None:
        selected = selected_location is None
      else:
        selected = (selected_location or '').strip().lower() == location.strip().lower()
      button.appearance = 'filled' if selected else 'outlined'

  def recent_events_click(self, **event_args):
    self.past_events = False
    self.update_admin_filter_buttons()
    self.load_events()

  def past_events_click(self, **event_args):
    self.past_events = True
    self.update_admin_filter_buttons()
    self.load_events()

  def new_event_click(self, **event_args):
    open_form("EditEvent", admin=True, past_events=self.past_events)

  def update_admin_filter_buttons(self):
    if self.past_events:
      self.recent_events_button.appearance = 'outlined'
      self.past_events_button.appearance = 'filled'
    else:
      self.recent_events_button.appearance = 'filled'
      self.past_events_button.appearance = 'outlined'

  def show_location(self, location):
    self.selected_location = location
    self.update_location_filter_buttons(location)
    if location:
      normalized_location = location.strip().lower()
      events = [event for event in self.all_events
                if (event['location'] or '').strip().lower() == normalized_location]
    else:
      events = self.all_events

    self.events_list.items = events
