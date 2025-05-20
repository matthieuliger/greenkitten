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


def extract_text_from_pdf_pypdf2(pdf_media):
  if not pdf_media.content_type.startswith("application/pdf"):
    raise ValueError("Not a PDF file")
  else:
    print("PDF file")

  # Get bytes from the Anvil media object
  try:
    with pdf_media.get_bytes() as f:
        pdf_file = io.BytesIO(f.read())
  except Exception as e:
      print("Error trying to read file with io")
      print(e)
      
  try:
    # Read with PyPDF2
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
      text += page.extract_text() or ""  # Handle pages with no extractable text
  except Exception as e:
    print("Error trying to read with PdfReader")
    print(e)
    
  return text