from ._anvil_designer import ChatTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
from anvil.js import get_dom_node
import json

class Chat(ChatTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print("Chat __init__")
    self.init_components(**properties)
    
    node = get_dom_node(self.pika_box)
    node.style.border = "1px solid black"
    node.style.padding = "2px"      # optional, makes it look nicer

    node = get_dom_node(self.grid_panel_2)
    node.style.border = "1px solid black"
    node.style.padding = "2px"      # optional, makes it look nicer

    
    # Check login status
    logged_in_user = anvil.users.get_user()
    
    if logged_in_user is not None:
      # There *is* a logged-in user
      self.login_status.text = f"{logged_in_user['email']} logged in"
      anvil.server.call("clear_history")
      print(f"{logged_in_user['email']} is logged in")
      #self.user_label.text = logged_in_user["email"]
      anvil.server.call("clear_history")
      print("getting first question")
      self.pika_box.content = anvil.server.call("get_first_question")
      
    else:
      # No one’s logged in
      self.login_status.text = "You are not logged in."
      print("No user logged in, opening Login form")
      open_form("Login")

  def user_box_change(self, **event_args):
    #print("user_box_change")
    if len(self.user_box.text) > 0:
      last = self.user_box.text[-1]
      #print("last character", last)
      if last == "\n":
        self.submit()
        self.user_box.text = ""

  def show_history(self):
    self.history_box.text = json.dumps(
      anvil.server.call("get_history"), indent=4)
  
  def submit(self, **event_args):
    print("submit")
    response = anvil.server.call("get_next", self.user_box.text)
    print(f"response to latest user's input: {response}")

    if 'done' in response.lower():
      print("The coach is done collecting information")
      self.show_history()
      self.user_box.text = ""
      self.pika_box.content = "Ok. I will now work on finding you a job"
      self.user_box.enabled = False
      anvil.server.call('save_history')
      leads = anvil.server.call('find_leads')
      self.pika_box.content = leads      
      
    else:
      self.pika_box.content = response
      self.show_history()
      self.user_box.text = ""

  def logout_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    logged_in_user = anvil.users.get_user()
    if logged_in_user is not None:
      # logged_in_user = anvil.users.get_user()
      # There is a logged-in user
      print(f"{logged_in_user['email']} is logged in")
      self.login_status.text = f"{logged_in_user['email']}"
    else:
      # No one’s logged in
      self.login_status.text = "You are not logged in."
      open_form("Login")
