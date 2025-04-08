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
    self.evento_text.content = properties.get("event_title")
    self.defaults = anvil.server.call("load_defaults")
    self.name_text.text = self.defaults.get("name", "")
    self.email_text.text = self.defaults.get("email", "")
    role = self.defaults.get("role", "genitore")
    if role == "genitore":
      self.genitore_radio.selected = True
      self.clan_radio.selected = False
    else:
      self.genitore_radio.selected = False
      self.clan_radio.selected = True
  def iscriviti_button_click(self, **event_args):
    if self.genitore_radio.selected:
      role = "genitore"
    else:
      role = "clan"
    anvil.server.call('sign_up', self.event_id,
                      self.name_text.text,
                      self.email_text.text,
                      role)
    alert("Thanks for signing up!")
    open_form("EventsForm")
