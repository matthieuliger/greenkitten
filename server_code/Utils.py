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
  if not pdf_media.content_type.startswith("application/pdf"):
    raise ValueError("Not a PDF file")
  else:
    print("PDF file")
  try:
    with pdf_media.get_bytes() as f:
      try:
        reader = PdfReader(io.BytesIO(f))  # No need to wrap in BytesIO
      except Exception as e:
        print("PdfReader or BytesIO error")
        print(e)
      print("extracting pages")
      text = ""
      for page in reader.pages:
        text += page.extract_text() or ""
        return text
  except Exception as e:
    print("Error trying to convert")
    print(e)
    traceback.print_exc()