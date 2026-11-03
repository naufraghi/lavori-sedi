from ._anvil_designer import EventsFormTemplate
from anvil import *
import anvil.server


class EventsForm(EventsFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.admin = properties.get('admin', False)
    self.requested_location = properties.get('location')
    self.past_events = properties.get('past_events', False)
    self.location_picker.visible = not self.admin
    self.recent_events_button.visible = self.admin
    self.past_events_button.visible = self.admin
    self.new_event_button.visible = self.admin
    self.update_admin_filter_buttons()
    self.load_events()

  def load_events(self):
    if self.admin:
      self.all_events = anvil.server.call('get_all_events', self.past_events)
      for event in self.all_events:
        event['past_events'] = self.past_events
      self.events_list.items = self.all_events
      return

    self.locations = anvil.server.call('get_event_locations')
    self.all_events = anvil.server.call('get_upcoming_events')

    self.location_picker.items = self.locations
    self.location_picker.visible = bool(self.locations)

    if self.requested_location in self.locations:
      selected_location = self.requested_location
    elif self.locations:
      selected_location = self.locations[0]
    else:
      selected_location = None

    self.location_picker.selected_value = selected_location
    self.show_location(selected_location)

  def location_picker_change(self, **event_args):
    self.show_location(self.location_picker.selected_value)

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
    if location:
      normalized_location = location.strip().lower()
      events = [event for event in self.all_events
                if (event['location'] or '').strip().lower() == normalized_location]
    else:
      events = self.all_events

    self.events_list.items = events
