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
        self.participants.content = "👥 " + ", ".join(self.item['participants'])

    def sign_up_btn_click(self, **event_args):
        # Open modal to sign up, passing the event ID
        open_form('SignupForm', event_id=self.item['id'])

    def confirm_button_click(self, **event_args):
        anvil.server.call('sign_up', self.event_id, self.name_tb.text, self.email_tb.text)
        alert("Thanks for signing up!")
        self.raise_event("x-close")  # if you're using modal popups