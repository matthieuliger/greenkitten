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
    return text
  except Exception as e:
    print("Error getting pages")
    print(e)
