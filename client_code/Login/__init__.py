from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class Login(LoginTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print("Login __init__")
    self.init_components(**properties)

  def login_with_link_click(self, **event_args):
    print("send_login_link_click")
    email = self.email_address.text.strip()
    try:
      anvil.server.call('send_sign_in_link', email)
      Notification("Check your inbox!").show()
    except Exception as e:
      Notification(f"Error: {e}").show()

  def signup_with_google_click(self, **event_args):
    print("signup_with_google_click")
    anvil.users.signup_with_google()
  
  def login_with_google_click(self, **event_args):
    print("login_with_google_click")
    anvil.users.login_with_google()
    if anvil.users.get_user():
      logged_in_user = anvil.users.get_user()
      # There *is* a logged-in user
      print(f"{logged_in_user['email']} is logged in")
      print("Opening Chat form")
      open_form('Chat')

  def signup_with_form_click(self, **event_args):
    print("signup_with_form_click")
    anvil.users.signup_with_form()

  def login_with_form_click(self, **event_args):
    print("login_with_form_click")
    anvil.users.login_with_form()
    print("Opening chat form after logging from form")
    open_form('Chat')