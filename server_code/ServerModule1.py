import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import openai
from PyPDF2 import PdfReader
import io
import anvil.server, anvil.secrets, openai

list_of_pieces_of_information_to_get = [
  "name",
  "location",
  "skills",
  "experience"
]

client = openai.OpenAI(api_key=anvil.secrets.get_secret("OPENAI_API_KEY"))

@anvil.server.callable
def clear_history():
  """Clear the history of the conversation."""
  print("clear_history")
  anvil.server.session["history"] = _init_history()
  return anvil.server.session["history"]

@anvil.server.callable
def send_sign_in_link(email):
  print("sending login link")
  anvil.users.send_token_login_email(email)

def _init_history():
  print("_init_history")
  return [
    {
      "role": "system",
      "content": "You are a career coach helping a client trying to "
      + "find a new job. You will ask the user questions, then later "
      + "we will look for startups which may have openings suitable "
      + "for the client. Keep asking question until you have answers to the following :"
      + ", ".join(list_of_pieces_of_information_to_get),
    },
    {"role": "assistant", "content": "Hello! What is your name?"},
  ]


@anvil.server.callable
def get_first_question():
  print("get_first_question")
  if "history" not in anvil.server.session:
    anvil.server.session["history"] = _init_history()
    # Return just the assistant’s first question:
  first_question = anvil.server.session["history"][1]["content"]
  print(f"First question:{first_question}")
  return first_question


@anvil.server.callable
def get_history():
  print("get_history")
  return anvil.server.session["history"]


@anvil.server.callable
def get_next(user_input):
  print("get_next")
  session_history = anvil.server.session["history"]

  session_history.append({"role": "user", "content": user_input})
  resp = client.chat.completions.create(
    model="gpt-3.5-turbo", messages=session_history
  )
  next_q = resp.choices[0].message.content
  session_history.append({"role": "assistant", "content": next_q})
  return next_q

def input_box_change(self, **event_args):
  """This method is called when the text in this text area is edited"""
  print(event_args)
  if len(self.input_box.text) > 0:
    last = self.input_box.text[-1]
    print("last character", last)
    if last == "\n":
      self.submit_button_click()
      self.input_box.text = ""

@anvil.server.callable
def extract_and_store_pdf(file_media):
  print("extract_and_store")
  # Read PDF bytes
  pdf_bytes = file_media.get_bytes()

  # Extract text
  reader = PdfReader(io.BytesIO(pdf_bytes))
  full_text = []
  for page in reader.pages:
    full_text.append(page.extract_text() or "")
  resume_text = "\n\n".join(full_text)

  # Store in the database
  logged_in_user = anvil.users.get_user()
  if logged_in_user is not None:
    # logged_in_user = anvil.users.get_user()
    # There is a logged-in user
    row = app_tables.users.get(
      app_tables.users.name == logged_in_user["email"]
    )
    if row is not None:
      # There is a row for this user
      row["resume"] = resume_text
      print(f"Resume stored for {logged_in_user['email']}")
      return True
    else:
      error_message = (
        f"User {logged_in_user['email']} not found in the database"
      )
      print(error_message)
      return False

  else:
    print(
      error_message := "No user logged in, cannot store "
      + "PDF (this should not happen)"
    )
    return False
