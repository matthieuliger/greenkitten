import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from PyPDF2 import PdfReader
import io
import traceback

def extract_text_from_pdf_pypdf2(pdf_media):
  print(f"type of pdf media {type(pdf_media)}, {pdf_media}")
  if not pdf_media.content_type.startswith("application/pdf"):
    raise ValueError("Not a PDF file")
  else:
    print("PDF file")
    
  try:
    f =  pdf_media.get_bytes()
    print("Done getting bytes")
  except Exception as e:
    print("Error trying to get bytes")
    print(e)
    traceback.print_exc()
    
  try:
    reader = PdfReader(io.BytesIO(f))  # No need to wrap in BytesIO
  except Exception as e:
    print("PdfReader or BytesIO error")
    print(e)
    print("extracting pages")
  
  text = ""
  try:
    for page in reader.pages:
      text += page.extract_text() or ""
    displayed_characters= min(40, len(text))
    print(f"Returning {text[:displayed_characters]}")
    return text
  except Exception as e:
    print("Error getting pages")
    print(e)

def get_resume():
  print("get_resume")
  logged_in_user = anvil.users.get_user()
  if logged_in_user is not None:
    resume_row = app_tables.inline_attachments.get(
      sender=logged_in_user["email"]
    )
    if resume_row is None:
      print(f"No resume found for {logged_in_user['email']}")
      resume = ""
    else:
      print("Resume available")
      resume = resume_row["extracted_text"]
      print(resume)
      return resume
  else:
    print("No user logged in, no resume to return.")
    return ""

