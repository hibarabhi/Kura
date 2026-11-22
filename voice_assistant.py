
# voice_assistant.py : bouton flottant (comme Messenger) pour parler à l'assistant Kura
#
# Comment ça marche :
#   - voice_widget_frontend/index.html dessine le bouton et le panneau sur le côté de la page.
#     Il écoute avec le micro du navigateur (Web Speech API) et lit la réponse à voix haute.
#   - Quand l'utilisateur parle ou écrit, le texte revient ici (Python).
#   - Python demande la réponse à Gemini (ai_chat.py) : la clé reste sur le serveur,
#     elle n'est jamais envoyée au navigateur.
import os

import streamlit as st
import streamlit.components.v1 as components

from ai_chat import get_ai_reply

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_widget_frontend")
_widget = components.declare_component("kura_voice_widget", path=FRONTEND_DIR)

# Le composant n'a pas d'interface à lui : le bouton est ajouté à la page par son JavaScript.
# On cache donc son cadre pour qu'il ne prenne aucune place.
HIDE_HOST = """
<style>
.st-key-kura_voice_host {
    position: fixed !important; width: 0 !important; height: 0 !important;
    overflow: hidden !important; opacity: 0; pointer-events: none;
}
</style>
"""

MAX_MESSAGE_CHARS = 500   # on coupe les messages trop longs
MAX_HISTORY = 30          # on garde seulement les derniers messages


def show_voice_assistant(profile):
    history = st.session_state.setdefault("ai_history", [])   # liste de (rôle, texte)

    with st.container(key="kura_voice_host"):
        st.markdown(HIDE_HOST, unsafe_allow_html=True)
        event = _widget(
            history=[[role, text] for role, text in history],
            reply=st.session_state.get("ai_reply"),
            key="kura_voice",
            default=None,
        )

    # Un nouveau message vient du navigateur ? (l'id évite de répondre deux fois au même)
    if event and event.get("id") != st.session_state.get("ai_last_event"):
        st.session_state["ai_last_event"] = event["id"]
        text = str(event.get("text", "")).strip()[:MAX_MESSAGE_CHARS]
        if text:
            history.append(("user", text))
            history.append(("assistant", get_ai_reply(history, profile)))
            del history[:-MAX_HISTORY]
            st.session_state["ai_reply"] = {
                "id": event["id"],
                "speak": bool(event.get("voice")),      # lire à voix haute seulement si on a parlé
                "lang": event.get("lang", "en-US"),
            }
            st.rerun()


def reset_voice_assistant():
    '''À appeler quand l'utilisateur se déconnecte.'''
    for key in ("ai_history", "ai_reply", "ai_last_event"):
        st.session_state.pop(key, None)

