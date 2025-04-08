from ._anvil_designer import EventCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class EventCard(EventCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.item = properties.get("item")
    self.populate()

  def populate(self):
    timestamp = f"{self.item['start'].strftime('%a %d %b, %H:%M')} - {self.item['end'].strftime('%H:%M')}"
    self.title.content = f"## 🧰 {self.item['title']} | 🗓 {timestamp} | 📍 {self.item['location']}"
    self.description.content = self.item['description']
    participants = []
    for p in self.item['participants']:
      participants.append(f"{p['name']} ({p['role']})")
    self.participants.content = "👥 " + ", ".join(participants)

  def signup_click(self, **event_args):
    # Open modal to sign up, passing the event ID
    open_form('SignupForm',
              event_id=self.item['id'],
              event_title=self.title.content)
