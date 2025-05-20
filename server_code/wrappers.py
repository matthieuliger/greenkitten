import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import openai

from .utils import get_resume

# model_chat = "gpt-3.5-turbo"
model_chat = "o4-mini-2025-04-16"
model_leads = "gpt-4o-2024-08-06"
client = openai.OpenAI(api_key=anvil.secrets.get_secret("OPENAI_API_KEY"))

list_of_pieces_of_information_to_get = [
  "What is the user's desired job location(s)?",
  "What are the users' skills?",
  "What are the user's values?",
  "Is the user looking to change careers, or stay in the same field?",
  "What is the user's desired salary range?",
  "Assuming we already know the main field the user wants to find a job in, is there a preferred subfield?"
  "Does the user want to share more information about the desired job or company?",
]

coach_persona_definition =  (
  "You are a career coach helping a client trying to "
  + "find a new job in a startup.\n"
)

coach_instructions = (
  "You will ask the user questions to help scope, then "
  + "we will look for startups which may have openings suitable "
  + "for the user.\n"
  + "- Keep asking question until you have answers to "
  + "the following, either from the resume or from the chat you have "
  + "with the user. That is, if you already have the information from "
  + "the resume, do not ask again, except to clarify things in the resume. \n"
  + "- Feel free to ask more question as you see fit, "
  + "anything you feel might make you more efficient at finding jobs "
  + "for the user, in startups.\n"
  + "- Just ask one question at a time."
)

original_lead_prompt = (
  "You are a career coach. Given the following information,"
  + "find startups in a relevant region. Feel free to look online."
  + " - Use crunchbase to find startups that"
  + " have had significant fundraising.\n"
  + " - Use pitchbook to find startups that"
  + " have had significant fundraising.\n"
  + "- Look on linkedin, "
  + "especially if you see either job ads or posts. "
  + "- Look in news stories, especially if the stories mention growth or product releases.\n"
  + "- For publicly-traded companies prioritize those with large stock price growth "
  + "(but also return startups that are pre-IPO)\n"
  + "Return:\n"
  + "- A list of companies, with some information about what they do, their size, funding status etc\n"
  + "- A list of key people the user could contact\n"
  + "- Relevant news stories about the companies or the field, in the geographic area(s) that are relevant\n"
)

def init_history():
  original_prompt = coach_persona_definition

  resume = get_resume()
  if resume:
    original_prompt += f"We already have the user's resume:\n {resume}.\n\n"
  
  original_prompt += coach_instructions

  original_prompt += "\n - ".join(list_of_pieces_of_information_to_get)

  # resume = get_resume()
  # if len(resume) > 1:
  #  original_prompt += original_prompt + resume

  original_prompt += (
    "When you are done, just answer 'DONE' (and nothing else)."
  )
  return [
    {
      "role": "system",
      "content": original_prompt,
    },
    {"role": "assistant", "content": "Hello! What is your name?"},
  ]

