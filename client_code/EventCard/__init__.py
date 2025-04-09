from ._anvil_designer import EventCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

ITALIAN_LOCALE = {
  # Months
  "Jan": "Gen",
  "Feb": "Feb",
  "Mar": "Mar",
  "Apr": "Apr",
  "May": "Mag",
  "Jun": "Giu",
  "Jul": "Lug",
  "Aug": "Ago",
  "Sep": "Set",
  "Oct": "Ott",
  "Nov": "Nov",
  "Dec": "Dic",
  
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
    self.populate()

  def populate(self):
    timestamp = localize_date(f"{self.item['start'].strftime('%a %d %b, %H:%M')} - {self.item['end'].strftime('%H:%M')}")
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
