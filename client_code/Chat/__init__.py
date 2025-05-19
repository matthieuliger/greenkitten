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
    self.init_components(**properties)
    
    # Check login status
    logged_in_user = anvil.users.get_user()
    
    if logged_in_user is not None:
      # There *is* a logged-in user
      self.login_status.text = f"{logged_in_user['email']} logged in"
      print(f"{logged_in_user['email']} is logged in")
      self.user_label.text = logged_in_user["email"]
      anvil.server.call("clear_history")
      self.pika_text_box.text = anvil.server.call("get_first_question")
    else:
      # No one’s logged in
      self.login_status.text = "You are not logged in."
      print("No user logged in, opening Login form")
      open_form("Login")