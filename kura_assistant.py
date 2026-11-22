# kura_assistant.py : bulle flottante "assistant IA" avec micro + texte  (Frontend 1)
#
# - un rond bleu en bas à droite ; au clic, une petite fenêtre s'ouvre (clic à côté = fermer)
# - 🎤 on parle (enregistreur natif de Streamlit, fonctionne avec le micro du navigateur)
# - Gemini comprend l'audio directement et répond ; 🔊 pour écouter la réponse
# - urgence -> 911 tout de suite ; si l'IA ne répond pas -> réponses par mots-clés
import base64
import hashlib
import html
import json
import time

import requests
import streamlit as st
import streamlit.components.v1 as components

from clinic_chat import RULES, get_reply as keyword_reply
from schedule import get_todays_reminders, get_upcoming_appointments

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash"]

SYSTEM_PROMPT = """You are Kura's friendly voice assistant for "Demo Health Clinic".
Kura helps patients with appointments, medication reminders, prescriptions, rides and caregivers.

You can help with:
- the patient's appointments (listed below), booking (Book tab), rescheduling (call the clinic, then "Update appointment")
- asking someone for a ride ("Ask for a ride" on an appointment, or the Rides service)
- medication reminders and prescriptions (Meds tab)
- linking a caregiver (Profile tab, share the KURA code)
- clinic info: open Monday to Friday, 8:00 to 17:00, phone 514-555-0123

Strict rules:
- Never diagnose, never suggest or change a medication or a dose, never give medical advice.
- For health questions, tell them to ask their doctor or pharmacist, or call Info-Santé at 811 (Québec).
- If anything sounds like an emergency, tell them to call 911 right away.
- Answers are read aloud: keep them short (1 to 3 sentences), warm, simple, no lists, no emojis.
- Reply in the same language as the patient.
"""

AUDIO_INSTRUCTION = ("The patient sent a voice message. Answer in exactly this format:\n"
                     "HEARD: <the exact words the patient said>\n"
                     "REPLY: <your answer>")

WELCOME = "Hi! I'm Kura's assistant. Tap the microphone and talk to me, or type a question."


# ---------------------------------------------------------------- IA
def _secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return None


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


def _emergency(text):
    words, reply = RULES[0]     # 1re règle de clinic_chat = urgence
    found = set("".join(c if c.isalnum() else " " for c in text.lower()).split())
    return reply if found & set(words) else None


def _call_gemini(contents, system):
    """Essaie plusieurs modèles ; réessaie une fois si Google est surchargé."""
    key = _secret("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("no GEMINI_API_KEY in .streamlit/secrets.toml")
    models = [_secret("GEMINI_MODEL")] + GEMINI_MODELS if _secret("GEMINI_MODEL") else GEMINI_MODELS
    last_error = "unknown error"
    for model in dict.fromkeys(models):
        for attempt in range(2):
            body = {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.4,
                                     "thinkingConfig": {"thinkingLevel": "low"}},
            }
            try:
                r = requests.post(GEMINI_URL.format(model=model),
                                  headers={"x-goog-api-key": key}, json=body, timeout=60)
                if r.status_code == 400 and "think" in r.text.lower():
                    body["generationConfig"].pop("thinkingConfig")
                    r = requests.post(GEMINI_URL.format(model=model),
                                      headers={"x-goog-api-key": key}, json=body, timeout=60)
            except requests.RequestException as error:
                last_error = str(error)[:120]
                break
            if r.status_code == 200:
                parts = r.json()["candidates"][0]["content"]["parts"]
                text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
                if text:
                    return text
                last_error = f"{model}: empty answer"
                break
            last_error = f"{model}: error {r.status_code}"
            if r.status_code == 503 and attempt == 0:
                time.sleep(1.5)
                continue
            break
    raise RuntimeError(last_error)


def _history_contents(history):
    contents = [{"role": "model" if role == "assistant" else "user",
                 "parts": [{"text": text.replace("🎤 ", "")}]}
                for role, text in history[-10:]]
    while contents and contents[0]["role"] != "user":
        contents.pop(0)
    return contents


def ask_text(question, history, profile):
    urgent = _emergency(question)
    if urgent:
        return urgent
    try:
        contents = _history_contents(history + [("user", question)])
        return _call_gemini(contents, SYSTEM_PROMPT + "\n\n" + _patient_context(profile))
    except Exception:
        return keyword_reply(question, profile)


def ask_audio(audio_bytes, history, profile):
    """Renvoie (ce que l'IA a entendu, réponse)."""
    audio_part = {"inline_data": {"mime_type": "audio/wav",
                                  "data": base64.b64encode(audio_bytes).decode()}}
    contents = _history_contents(history) + [
        {"role": "user", "parts": [audio_part, {"text": AUDIO_INSTRUCTION}]}]
    try:
        text = _call_gemini(contents, SYSTEM_PROMPT + "\n\n" + _patient_context(profile))
    except Exception:
        return None, "Sorry, I couldn't process your voice right now. You can type your question below."

    heard, reply = None, text
    if "REPLY:" in text:
        before, reply = text.split("REPLY:", 1)
        heard = before.replace("HEARD:", "").strip() or None
        reply = reply.strip()
    urgent = _emergency(heard or "")
    return heard, (urgent or reply)


# ---------------------------------------------------------------- interface
def _looks_french(text):
    t = f" {text.lower()} "
    return sum(w in t for w in (" je ", " vous ", " votre ", " rendez", " est ", " le ", " la ",
                                " bonjour", " merci", " pour ", " avec ")) >= 2


def _listen_button(text):
    """Bouton 🔊 (le navigateur lit la réponse à voix haute après un clic)."""
    lang = "fr-FR" if _looks_french(text) else "en-US"
    components.html(
        f"""<button id="k" style="border:none;border-radius:999px;padding:8px 16px;cursor:pointer;
        font:600 14px sans-serif;color:#1D4ED8;background:#EAF1FF">🔊 Listen</button>
        <script>
        const t = {json.dumps(text)};
        document.getElementById("k").onclick = () => {{
            speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(t); u.lang = "{lang}"; u.rate = 1;
            speechSynthesis.speak(u);
        }};
        </script>""",
        height=46,
    )


def reset_assistant():
    for k in ("ai_msgs", "ai_last_audio", "ai_audio_n", "ai_speak"):
        st.session_state.pop(k, None)


def show_assistant(profile):
    ss = st.session_state
    ss.setdefault("ai_msgs", [("assistant", WELCOME)])
    ss.setdefault("ai_audio_n", 0)

    with st.container(key="aifab"):
        with st.popover("Assistant"):
            st.markdown(
                '<div class="ka-head"><div class="ka-dot">✦</div>'
                '<div><b>Kura Assistant</b><small>Voice & chat · demo</small></div></div>',
                unsafe_allow_html=True,
            )

            bubbles = "".join(
                f'<div class="ka-b {"me" if role == "user" else "ai"}">{html.escape(text)}</div>'
                for role, text in ss["ai_msgs"][-8:]
            )
            st.markdown(f'<div class="ka-msgs">{bubbles}</div>', unsafe_allow_html=True)

            if ss.get("ai_speak"):
                _listen_button(ss["ai_speak"])

            # 🎤 enregistrement (la clé change après chaque message -> enregistreur remis à zéro)
            audio = st.audio_input("Tap the mic and talk", key=f'ai_audio_{ss["ai_audio_n"]}')
            if audio is not None:
                data = audio.getvalue()
                digest = hashlib.md5(data).hexdigest()
                if ss.get("ai_last_audio") != digest:
                    ss["ai_last_audio"] = digest
                    with st.spinner("Listening..."):
                        heard, reply = ask_audio(data, ss["ai_msgs"], profile)
                    ss["ai_msgs"].append(("user", "🎤 " + (heard or "(voice message)")))
                    ss["ai_msgs"].append(("assistant", reply))
                    ss["ai_speak"] = reply
                    ss["ai_audio_n"] += 1
                    st.rerun()

            # ⌨️ ou écrire
            with st.form("ai_text_form", clear_on_submit=True):
                question = st.text_input("Message", placeholder="Or type a question...",
                                         label_visibility="collapsed")
                sent = st.form_submit_button("Send")
            if sent and question.strip():
                with st.spinner("Thinking..."):
                    reply = ask_text(question.strip(), ss["ai_msgs"], profile)
                ss["ai_msgs"].append(("user", question.strip()))
                ss["ai_msgs"].append(("assistant", reply))
                ss["ai_speak"] = reply
                st.rerun()

            if len(ss["ai_msgs"]) > 1 and st.button("Clear conversation", key="ai_clear"):
                reset_assistant()
                st.rerun()

            st.caption("Not for emergencies: call 911. No medical advice.")