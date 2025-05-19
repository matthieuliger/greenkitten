from ._anvil_designer import ChatTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class Chat(ChatTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print("Chat __init__")
    self.init_components(**properties)
    
    # Check login status
    logged_in_user = anvil.users.get_user()
    
    if logged_in_user is not None:
      # There *is* a logged-in user
      self.login_status.text = f"{logged_in_user['email']} logged in"
      print(f"{logged_in_user['email']} is logged in")
      self.user_label.text = logged_in_user["email"]
      anvil.server.call("clear_history")
      print("getting first question")
      self.pika_box.text = anvil.server.call("get_first_question")
      
    else:
      # No one’s logged in
      self.login_status.text = "You are not logged in."
      print("No user logged in, opening Login form")
      open_form("Login")

  def user_box_change(self, **event_args):
    print("user_box_change")
    if len(self.user_box.text) > 0:
      last = self.user_box.text[-1]
      print("last character", last)
      if last == "\n":
        self.submit_button_click()
        self.user_box.text = ""

  def submit_button_click(self, **event_args):
    print("submit_button_click")
    # anvil.server.call("add_to_history", {"user": self.input_box.text})
    response = anvil.server.call("get_next", self.user_box.text)
    print(f"response to latest user's input: {response}")
    self.pika_box.text = response

    self.history_box.text = anvil.server.call("get_history")
    # print(f"History: {anvil.server.call("get_history")}")
    self.input_box.text = ""
