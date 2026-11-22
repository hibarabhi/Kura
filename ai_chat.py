# ai_chat.py : assistant IA (Gemini, palier gratuit) avec plan B par mots-clés
import os
import re

import streamlit as st

from clinic_chat import get_reply
from schedule import get_todays_reminders, get_upcoming_appointments

try:
    from google import genai
    from google.genai import types
except ImportError:  # library not installed: we use the keyword chat instead
    genai = None

# Google recommends the 3.x Flash models for new projects ("gemini-2.5-flash" is only served
# to accounts that already used it). Flash-Lite is the lightest one. Model names change often:
# to switch without touching the code, add GEMINI_MODEL = "..." to your secrets.
DEFAULT_MODEL = "gemini-3.5-flash-lite"

EMERGENCY_WORDS = {
    "emergency", "urgence", "urgent", "911",
    "chest", "breathe", "poitrine", "respirer",
}
EMERGENCY_REPLY = "🚨 If this is an emergency, call 911 right now."

APP_GUIDE = """You are Kura's assistant. Kura is a health-tracking app for older adults.
You help the user use the app and answer questions about their own appointments and reminders.

How the app works:
- A bottom bar has four pages: Home, Book, Chat, Profile.
- Home: a search bar, a "Book Now" button, four service buttons (Rides, Medication,
  Caregiver, Messages), today's reminders (tick the box once the medication is taken),
  and upcoming appointments. Under each appointment there are three sections:
  "Ask for a ride" (builds a message to copy and send), "Appointment notes",
  and "Update appointment" (change the date or time after the clinic confirms).
- Book: choose a date, an available hour and a doctor, then press "Book appointment".
  A week calendar shows the appointments.
- Chat: this conversation.
- Profile: shows a code to link a caregiver (family or friend), the list of linked people
  with a Remove button, and a Log out button.
- A caregiver does not need an account: on the first screen they open "I'm a caregiver"
  and enter the patient's code and their own name. They see a dashboard with alerts for
  missed medication and the upcoming appointments.
- To cancel or reschedule with the clinic, the user calls 514-555-0123, then updates the
  date in the app under "Update appointment".

Rules:
- Use short, simple sentences. Be warm and patient. Reply in the language the user writes in.
- Guide step by step: say which page and which button to use.
- You cannot change anything in the app yourself. Tell the user what to press.
- You are an app assistant, not clinic staff and not a doctor.
- Never give medical advice, diagnoses or medication doses. For medical questions say:
  "Please ask your doctor or pharmacist." For a non-urgent health question you can mention
  Info-Santé at 811.
- If the user describes an emergency (chest pain, cannot breathe, a fall, etc.), tell them
  to call 911 now.
- If you are not sure about something, say so. Do not invent features, data or appointments.
"""


def get_client():
    if genai is None:
        print("[Kura AI] The 'google-genai' package is not installed: using the keyword chat.")
        return None
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[Kura AI] No GEMINI_API_KEY found (secrets or environment): using the keyword chat.")
        return None
    return genai.Client(api_key=key)


def get_model():
    try:
        return st.secrets["GEMINI_MODEL"]
    except Exception:
        return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)


def build_system_prompt(profile):
    lines = [APP_GUIDE, f'The user\'s first name is {profile["name"]}.',
             "The user's current data (only use it to answer):"]
    for r in get_todays_reminders(profile["reminders"]):
        state = "taken" if r["taken"] else "not taken yet"
        lines.append(f'- Reminder today: {r["title"]} at {r["time"]} ({state})')
    for a in get_upcoming_appointments(profile["appointments"])[:3]:
        doctor = a.get("doctor", "the clinic")
        lines.append(
            f'- Appointment: {a["title"]} with {doctor} on {a["date"]} '
            f'at {a["time"]}, {a["location"]}'
        )
    return "\n".join(lines)


def get_ai_reply(history, profile):
    '''history is the list of (role, text) tuples of the chat, ending with the user's message.'''
    last = history[-1][1]

    # emergencies never go through the AI
    words = set(re.findall(r"[a-zàâçéèêëîïôûùüÿ0-9']+", last.lower()))
    if words & EMERGENCY_WORDS:
        return EMERGENCY_REPLY

    client = get_client()
    if client is None:
        return get_reply(last, profile)

    contents = [
        types.Content(
            role="user" if role == "user" else "model",
            parts=[types.Part(text=text)],
        )
        for role, text in history[-10:]  # only the last 10 messages
    ]
    # the conversation must start with a user message
    while contents and contents[0].role == "model":
        contents.pop(0)

    try:
        response = client.models.generate_content(
            model=get_model(),
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(profile),
                max_output_tokens=1024,  # room left for the model's internal thinking
            ),
        )
        return response.text or get_reply(last, profile)
    except Exception as error:
        # limit reached, wrong model name, no internet, etc.: fall back to the keyword chat.
        # The reason is printed in the server logs so the failure is not silent.
        print(f"[Kura AI] Gemini call failed ({type(error).__name__}): {error}")
        return get_reply(last, profile)
