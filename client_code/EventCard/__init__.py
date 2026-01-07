from ._anvil_designer import EventCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

ITALIAN_LOCALE = {
  # Months
  "Jan,": "Gen,",
  "Feb,": "Feb,",
  "Mar,": "Mar,",
  "Apr,": "Apr,",
  "May,": "Mag,",
  "Jun,": "Giu,",
  "Jul,": "Lug,",
  "Aug,": "Ago,",
  "Sep,": "Set,",
  "Oct,": "Ott,",
  "Nov,": "Nov,",
  "Dec,": "Dic,",
  
  # Weekdays
  "Mon": "Lun",
  "Tue": "Mar",
  "Wed": "Mer",
  "Thu": "Gio",
  "Fri": "Ven",
  "Sat": "Sab",
  "Sun": "Dom",
}

def localize_date(message):
  words = message.split()
  for i, word in enumerate(words):
    words[i] = ITALIAN_LOCALE.get(word, word)
  return " ".join(words)

class EventCard(EventCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.item = properties.get("item")
    self.edit_button.visible = self.item['modify']
    self.signup.enabled = not self.item['hidden']
    self.populate()

  def populate(self):
    timestamp = localize_date(f"{self.item['start'].strftime('%a %d %b, %H:%M')} - {self.item['end'].strftime('%H:%M')}")
    self.title.content = f"## 🧰 {self.item['title']} | 🗓 {timestamp} | 📍 {self.item['location']}"
    self.description.content = self.item['description']
    participants = []
    for p in self.item['participants']:
      participants.append(f"{p['name']} ({p['role']})")
    manager = self.item['manager']
    if not manager:
      manager = '...'
    else:
      manager = f"{manager['name']} ({manager['role']})"
    self.participants.content = f"👷🏾 {manager} | 👥 " + ", ".join(participants)

  def signup_click(self, **event_args):
    # Open modal to sign up, passing the event ID
    open_form('SignupForm',
              event_id=self.item['id'],
              event_title=self.title.content)

  def edit_button_click(self, **event_args):
    event = anvil.server.call("get_event", self.item['id'])
    open_form('EditEvent',
              event_id=self.item['id'],
              item=event)
