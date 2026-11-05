import locale

locale.setlocale(locale.LC_TIME, "it-IT-u-fw-mon")

from ._anvil_designer import EventsFormTemplate
from anvil import *
import anvil.server
from m3.components import Button as M3Button

LOCATION_COLORS = [
  'var(--anvil-m3-surface-container-low)',  # Keep the existing To1 card color.
  '#E3F2FD',  # Light blue
  '#FCE4EC',  # Light pink
  '#E8F5E9',  # Light green
  '#FFF3E0',  # Light orange
  '#EDE7F6',  # Light purple
  '#E0F7FA',  # Light cyan
  '#F9FBE7',  # Light lime
  '#FBE9E7',  # Light coral
  '#E8EAF6',  # Light indigo
]

LOCATION_COLOR_INDICES = {
  'to1': 0,
  'to2': 1,
  'to3': 2,
  'to4': 3,
  'to5': 4,
}


def location_key(location):
  return location.split()[-1].lower()


def get_location_colors(locations):
  colors = {}
  next_index = len(LOCATION_COLOR_INDICES)

  for location in locations:
    key = location_key(location)
    if not key or key in colors:
      continue

    if key in LOCATION_COLOR_INDICES:
      color_index = LOCATION_COLOR_INDICES[key]
    else:
      color_index = next_index % len(LOCATION_COLORS)
      next_index += 1
    colors[key] = LOCATION_COLORS[color_index]

  return colors


class EventsForm(EventsFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.admin = properties.get('admin', False)
    self.requested_location = properties.get('location')
    self.selected_location = self.requested_location
    self.past_events = properties.get('past_events', False)
    self.admin_toolbar_card.visible = self.admin
    self.location_filter_panel.visible = True
    self.location_filter_buttons = []
    self.update_admin_filter_buttons()
    self.load_events()

  def load_events(self):
    self.locations = anvil.server.call('get_event_locations')
    location_colors = get_location_colors(self.locations)

    if self.admin:
      self.all_events = anvil.server.call('get_all_events', self.past_events)
      for event in self.all_events:
        event['past_events'] = self.past_events
    else:
      self.all_events = anvil.server.call('get_upcoming_events')

    for event in self.all_events:
      event['location_color'] = location_colors.get(
        location_key(event['location']), LOCATION_COLORS[0]
      )

    self.location_filter_panel.clear()
    self.location_filter_buttons = []
    self.add_location_filter_button('Tutte le sedi', None)
    for location in self.locations:
      self.add_location_filter_button(location, location)

    self.selected_location = self.resolve_location(self.selected_location)

    self.show_location(self.selected_location)

  def resolve_location(self, location):
    if not location:
      return None

    normalized_location = location.strip().lower()
    for actual_location in self.locations:
      actual_location_text = (actual_location or '').strip()
      if actual_location_text.lower() == normalized_location:
        return actual_location
      if actual_location_text and location_key(actual_location_text) == normalized_location:
        return actual_location
    return None

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
