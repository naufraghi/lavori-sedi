from ._anvil_designer import SignupFormTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SignupForm(SignupFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.event_id = properties.get("event_id")
    self.evento_text.content = properties.get("event_title") or ""
    self.location = properties.get("location")
    self.admin = properties.get("admin", False)
    self.past_events = properties.get("past_events", False)
    self.defaults = anvil.server.call("load_defaults")
    self.name_text.text = self.defaults.get("name", "")
    self.email_text.text = self.defaults.get("email", "")
    role = self.defaults.get("role", "genitore")
    if role == "clan":
      self.genitore_radio.selected = False
      self.clan_radio.selected = True
    else:
      self.genitore_radio.selected = True
      self.clan_radio.selected = False
    role = self._selected_role()
    if anvil.server.call('is_signed_up', self.event_id,
                        self.name_text.text,
                        self.email_text.text,
                        role):
      self.rimuovi_button.enabled = True
    else:
      self.rimuovi_button.enabled = False      

  def _selected_role(self):
    if self.clan_radio.selected:
      return "clan"
    return "genitore"

  def iscriviti_button_click(self, **event_args):
    role = self._selected_role()
    anvil.server.call('sign_up', self.event_id,
                      self.name_text.text,
                      self.email_text.text,
                      role)
    open_form("EventsForm", location=self.location, admin=self.admin,
              past_events=self.past_events)

  def indietro_button_click(self, **event_args):
    """This method is called when the component is clicked."""
    open_form("EventsForm", location=self.location, admin=self.admin,
              past_events=self.past_events)

  def rimuovi_button_click(self, **event_args):
    role = self._selected_role()
    anvil.server.call('sign_out', self.event_id,
                      self.name_text.text,
                      self.email_text.text,
                      role)
    open_form("EventsForm", location=self.location, admin=self.admin,
              past_events=self.past_events)
