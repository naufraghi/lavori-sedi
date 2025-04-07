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
        self.title.text = self.item['title']
        #self.datetime_label.text = f"{self.item['start'].strftime('%b %d, %H:%M')} - {self.item['end'].strftime('%H:%M')}"
        #self.location_label.text = f"📍 {self.item['location']}"
        self.description.text = self.item['description']
        self.participants.text = "👥 " + ", ".join(self.item['participants'])

    def sign_up_btn_click(self, **event_args):
        # Open modal to sign up, passing the event ID
        open_form('SignupForm', event_id=self.item['id'])

    def confirm_button_click(self, **event_args):
        anvil.server.call('sign_up', self.event_id, self.name_tb.text, self.email_tb.text)
        alert("Thanks for signing up!")
        self.raise_event("x-close")  # if you're using modal popups