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
from datetime import datetime
from .Utils import extract_text_from_pdf_pypdf2


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
  return [
    {
      "role": "system",
      "content": "You are a career coach helping a client trying to "
      + "find a new job. You will ask the user questions, then later "
      + "we will look for startups which may have openings suitable "
      + "for the client. Keep asking question until you have answers to the following :"
      + ", ".join(list_of_pieces_of_information_to_get)
      + "When you are done, just answer 'DONE' (and nothing else).",
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


@anvil.server.callable
def find_leads():
  logged_in_user = anvil.users.get_user()
  if logged_in_user is not None:  
    history_row = app_tables.chat_history.get(
      user = logged_in_user['email']
    )
    if history_row is None:
      return "No leads, you need to chat with me first!"
    else:
      print(f"Chat history for {logged_in_user['email']} found.")
      chat_history = history_row['chat_history']
      print(f"History: {json.dumps(chat_history[1:], indent=4)}")
    
  else:
    raise RuntimeError("Logged in user not found when calling 'find_leads', this should not happen")
    
  resume_row = app_tables.inline_attachments.get(
      sender = logged_in_user['email']
    )
  if resume_row is None:
    print(f"No resume found for {logged_in_user['email']}")
    resume = "(no resume)"
  else:
    resume = row['extracted_text']
  #chat_history = chat_history + {"user" : "this is my resume: {resume}"}

  leads_prompt = ("You are a career coach. Given the chat history:" + chat_history + "\n Find startups in a relevant region.")
  
  response = client.responses.create(
    model="gpt-4o-mini-2024-07-18",
    tools=[{"type": "web_search_preview"}],
    input=leads_prompt,
  )
  print(f"Leads: {response}")
  return response

@anvil.server.callable
def save_history():
  print("Save history")
  logged_in_user = anvil.users.get_user()
  if logged_in_user is not None:  
    row = app_tables.users.get(
      email = logged_in_user['email']
    )
    if row is None:
      raise RuntimeError("Logged in user not found, this should not happen")
    row = app_tables.chat_history.get(
      user = logged_in_user['email']
    )
    if row is not None:
      print(f"There was already history for user {logged_in_user['email']}, appending.")
      row['chat_history'] = row['chat_history'] + anvil.server.session["history"]
    else:
      print(f"There was no history for user {logged_in_user['email']}, initiating record in database.")
      app_tables.chat_history.add_row(
        user = logged_in_user['email'],
        chat_history = anvil.server.session["history"]
      )
  else:
    print("No user logged in, not saving")


@anvil.email.handle_message
def incoming_email(msg):
  print("incoming")
  try:
    app_tables.received_messages.add_row(
      from_addr=msg.envelope.from_address,
      to=msg.envelope.recipient,
      text=msg.text,
      html=msg.html,
    )
  except Exception as e:
    print("Something went wrong trying to save the incoming text\n")
    print(e)
    app_tables.errors.add_row(
      sender=msg.envelope.from_address,
      timestamp=datetime.now()
    )

  print("saved message")
  print(f"Text:{msg.text}")
  print(f"Length of attachments {len(msg.attachments)}")
  print(f"Length of inline attachments {len(msg.inline_attachments)}")
  print(f"type of inline attachment iterator {type(msg.inline_attachments)}")
  print(f"List:{list(msg.inline_attachments)}")
  
  for attachment in msg.attachments:
    print("Saving regular attachment")
    try:
      app_tables.attachments.add_row(
        attachment=attachment,
        sender=msg.envelope.from_address
      )
    except Exception as e:
      print("Something went wrong trying to save attachment\n")
      app_tables.errors.add_row(
        sender=msg.envelope.from_address,
        timestamp=datetime.now()
      )
      print(e)
      
  for content_id, media in msg.inline_attachments.items():
    print("Saving inline attachment")
    print(f"Media type: {media.content_type}")
    try:
      if media.content_type.startswith("application/pdf"):
        print("PDF detected")
        try:
          text = extract_text_from_pdf_pypdf2(media)
        except Exception as e:
          print("Error trying to extract text")
          print(e)
        row = app_tables.inline_attachments.get(
          sender = msg.envelope.from_address
        )
        if row is None:
          print("Sender does not have an attachment in the database")
          app_tables.inline_attachments.add_row(
            attachment=media,
            header=content_id,
            sender=msg.envelope.from_address,
            extracted_text=text,
          )
        else:
          print("Sender has an attachment in the database")
          row['attachment'] = media
          row['extracted_text'] = text
      else:
        print("PDF not detected")
        app_tables.inline_attachments.add_row(
          attachment=media,
          header=content_id,
          sender=msg.envelope.from_address
        )
      
    except Exception as e:
      print("Something went wrong trying to save inline attachment\n")
      print(e)
      app_tables.errors.add_row(
        sender=msg.envelope.from_address,
        timestamp=datetime.now()
      )