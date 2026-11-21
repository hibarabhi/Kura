# ai_chat.py : chatbot avec une vraie IA gratuite (Gemini ou Groq), avec le chat à mots-clés en secours
import time

import requests
import streamlit as st

from clinic_chat import RULES, get_reply as keyword_reply
from schedule import get_upcoming_appointments, get_todays_reminders

DEBUG = True   # affiche pourquoi l'IA ne répond pas (mettre False pour la démo)
GEMINI_MODEL = "gemini-3.8-flash"         # modèle Gemini (changeable dans secrets.toml)
# modèles de secours si le premier est surchargé ou introuvable
GEMINI_BACKUP_MODELS = ["gemini-3.8-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are the friendly assistant of "Demo Health Clinic" inside the Kura app.
Kura helps patients with appointments, medication reminders, rides to appointments and caregivers.

What you can help with:
- the patient's appointments (listed below), booking (Book tab), rescheduling (call the clinic, then use "Update appointment")
- asking someone for a ride ("Ask for a ride" on an appointment)
- medication reminders and prescriptions (Medication page)
- linking a caregiver (Profile tab, share the KURA code)
- clinic info: open Monday to Friday, 8:00 to 17:00, phone 514-555-0123

Strict rules:
- Never diagnose, never suggest or change a medication or a dose, never give medical advice.
- For health questions, tell them to ask their doctor or pharmacist, or call Info-Santé at 811 (Québec).
- If anything sounds like an emergency, tell them to call 911 right away.
- Keep answers short (2 to 4 sentences), warm and simple. Reply in the same language as the patient.
"""


def _patient_context(profile):
    lines = [f'Patient first name: {profile["name"]}']
    appts = get_upcoming_appointments(profile["appointments"])
    if appts:
        lines.append("Upcoming appointments:")
        for a in appts[:5]:
            lines.append(f'- {a["title"]} with {a.get("doctor", "the clinic")} on {a["date"]} '
                         f'at {a["time"]}, {a["location"]}')
    else:
        lines.append("No upcoming appointments.")
    today = get_todays_reminders(profile["reminders"])
    if today:
        lines.append("Today's medication reminders:")
        for r in today:
            lines.append(f'- {r["time"]} {r["title"]} ({"taken" if r["taken"] else "not taken yet"})')
    return "\n".join(lines)


def _is_emergency(message):
    # La 1re règle de clinic_chat est la règle "urgence" : on la vérifie AVANT l'IA
    emergency_words, emergency_reply = RULES[0]
    words = set(message.lower().replace("?", " ").replace("!", " ").replace(",", " ").split())
    return emergency_reply if words & set(emergency_words) else None


def _secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return None


def _check(response, name):
    if response.status_code != 200:
        try:
            detail = response.json().get("error", {}).get("message", "")
        except Exception:
            detail = response.text[:200]
        raise RuntimeError(f"{name} error {response.status_code}: {detail}")


def _gemini_reply(api_key, system, history, model):
    contents = [{"role": "model" if role == "assistant" else "user", "parts": [{"text": text}]}
                for role, text in history if role in ("user", "assistant")][-12:]
    while contents and contents[0]["role"] != "user":   # Gemini veut commencer par l'utilisateur
        contents.pop(0)
    if not contents:
        return None
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": contents,
        # "thinkingLevel: low" = l'IA réfléchit moins longtemps -> réponse plus rapide
        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.4,
                             "thinkingConfig": {"thinkingLevel": "low"}},
    }
    response = requests.post(GEMINI_URL.format(model=model),
                             headers={"x-goog-api-key": api_key}, json=body, timeout=60)
    if response.status_code == 400 and "think" in response.text.lower():
        # si ce modèle n'accepte pas ce réglage, on réessaie sans
        body["generationConfig"].pop("thinkingConfig")
        response = requests.post(GEMINI_URL.format(model=model),
                                 headers={"x-goog-api-key": api_key}, json=body, timeout=60)
    _check(response, "Gemini")
    parts = response.json()["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    return text or None


def _groq_reply(api_key, system, history):
    messages = [{"role": "system", "content": system}]
    messages += [{"role": role, "content": text}
                 for role, text in history if role in ("user", "assistant")][-12:]
    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": GROQ_MODEL, "messages": messages, "max_tokens": 300, "temperature": 0.4},
        timeout=20,
    )
    _check(response, "Groq")
    return response.json()["choices"][0]["message"]["content"]


def _ai_reply(history, profile):
    """Renvoie (réponse, erreur). Essaie plusieurs modèles Gemini, puis Groq."""
    system = SYSTEM_PROMPT + "\n\n" + _patient_context(profile)
    errors = []

    gemini_key = _secret("GEMINI_API_KEY")
    if gemini_key:
        models = [_secret("GEMINI_MODEL") or GEMINI_MODEL] + GEMINI_BACKUP_MODELS
        for model in dict.fromkeys(models):           # sans doublons, dans l'ordre
            for attempt in range(2):                  # 2 essais si le serveur est surchargé
                try:
                    reply = _gemini_reply(gemini_key, system, history, model)
                    if reply:
                        return reply, None
                    break
                except Exception as error:
                    message = str(error)
                    errors.append(f"{model}: {message[:90]}")
                    if "503" in message and attempt == 0:
                        time.sleep(1.5)               # surchargé : on réessaie une fois
                        continue
                    break                             # 404, 429... : modèle suivant

    groq_key = _secret("GROQ_API_KEY")
    if groq_key:
        try:
            return _groq_reply(groq_key, system, history), None
        except Exception as error:
            errors.append(f"groq: {str(error)[:90]}")

    if not gemini_key and not groq_key:
        return None, "no API key found in .streamlit/secrets.toml"
    return None, " | ".join(errors[-3:])


def smart_reply(message, history, profile):
    """1) urgence -> 911 tout de suite  2) IA  3) mots-clés si l'IA ne répond pas."""
    emergency = _is_emergency(message)
    if emergency:
        return emergency
    with st.spinner("Typing..."):
        reply, error = _ai_reply(history, profile)
    if reply:
        return reply
    fallback = keyword_reply(message, profile)
    if DEBUG and error:
        fallback += f"\n\n⚠️ AI not used: {error}"
    return fallback