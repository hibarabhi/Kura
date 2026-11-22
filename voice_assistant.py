# voice_assistant.py : bouton flottant (comme Messenger) pour parler à l'assistant Kura
#
# Comment ça marche :
#   - Le HTML/JavaScript (WIDGET_HTML, tout en bas de ce fichier) dessine le bouton et le panneau
#     sur le côté de la page.
#     Il écoute avec le micro du navigateur (Web Speech API) et lit la réponse à voix haute.
#   - Quand l'utilisateur parle ou écrit, le texte revient ici (Python).
#   - Python demande la réponse à Gemini (ai_chat.py) : la clé reste sur le serveur,
#     elle n'est jamais envoyée au navigateur.
import os
import tempfile

import streamlit as st
import streamlit.components.v1 as components

from ai_chat import get_ai_reply

_widget = None


def _get_widget():
    '''Écrit WIDGET_HTML (tout en bas du fichier) dans un dossier temporaire, puis déclare le composant.'''
    global _widget
    if _widget is None:
        folder = os.path.join(tempfile.gettempdir(), "kura_voice_widget")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        try:
            with open(path, encoding="utf-8") as f:
                same = f.read() == WIDGET_HTML
        except OSError:
            same = False
        if not same:
            with open(path, "w", encoding="utf-8") as f:
                f.write(WIDGET_HTML)
        _widget = components.declare_component("kura_voice_widget", path=folder)
    return _widget

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
        event = _get_widget()(
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


# ======================================================================
# Le bouton, le panneau, le micro et la voix (HTML + JavaScript). Pas besoin de le modifier.
# ======================================================================
WIDGET_HTML = r'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
/*
  Kura voice widget (no build step).
  - Speaks the Streamlit component protocol by hand (componentReady / render / setComponentValue).
  - Draws a floating button + chat panel on the side of the PARENT page, so it floats like Messenger.
  - Listens with the browser's Web Speech API and reads answers aloud with speechSynthesis.
  - The AI answer itself comes from Python (the Gemini key never reaches the browser).
*/
(function () {
  "use strict";

  var AUTO_LISTEN = true;   // tapping the floating button also starts the microphone
  var REPLY_TIMEOUT_MS = 45000;   // give up waiting for the AI after this long

  var P, D;
  try { P = window.parent; D = P.document; void D.body; } catch (err) { return; }

  // ---------- Streamlit protocol ----------
  function post(type, data) {
    var msg = { isStreamlitMessage: true, type: type };
    for (var k in data) { msg[k] = data[k]; }
    P.postMessage(msg, "*");
  }
  post("streamlit:componentReady", { apiVersion: 1 });
  post("streamlit:setFrameHeight", { height: 0 });

  // ---------- small helpers ----------
  function load(key) { try { return P.localStorage.getItem(key); } catch (e) { return null; } }
  function save(key, value) { try { P.localStorage.setItem(key, value); } catch (e) { /* ignore */ } }
  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }

  var TEXT = {
    en: {
      title: "Kura assistant",
      hello: "Hi! Tap the microphone and talk to me, or type your question.",
      placeholder: "Type a message…",
      listening: "Listening… speak now",
      thinking: "Thinking…",
      unsupported: "Voice input isn't supported in this browser. Try Chrome, Edge or Safari, or type your message.",
      denied: "The microphone is blocked. Allow it in the address bar, then try again.",
      nospeech: "I didn't hear anything. Tap the microphone and try again.",
      network: "Voice input needs an internet connection.",
      slow: "This is taking longer than usual. Please try again.",
      open: "Open the Kura assistant",
      close: "Close",
      mic: "Speak",
      send: "Send",
      soundOn: "Spoken answers: on",
      soundOff: "Spoken answers: off"
    },
    fr: {
      title: "Assistant Kura",
      hello: "Bonjour! Appuyez sur le micro pour me parler, ou écrivez votre question.",
      placeholder: "Écrivez un message…",
      listening: "Je vous écoute… parlez maintenant",
      thinking: "Je réfléchis…",
      unsupported: "La voix n'est pas prise en charge par ce navigateur. Essayez Chrome, Edge ou Safari, ou écrivez votre message.",
      denied: "Le micro est bloqué. Autorisez-le dans la barre d'adresse, puis réessayez.",
      nospeech: "Je n'ai rien entendu. Appuyez sur le micro et réessayez.",
      network: "La voix a besoin d'une connexion Internet.",
      slow: "Ça prend plus de temps que prévu. Veuillez réessayer.",
      open: "Ouvrir l'assistant Kura",
      close: "Fermer",
      mic: "Parler",
      send: "Envoyer",
      soundOn: "Réponses à voix haute : oui",
      soundOff: "Réponses à voix haute : non"
    }
  };

  var CSS = `
#kura-voice-root, #kura-voice-root * { box-sizing: border-box; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
#kura-voice-root button { font-family: inherit; }
#kura-voice-root .kv-fab {
  position: fixed; right: max(14px, calc(50vw - 196px)); bottom: 120px; z-index: 1000;
  width: 58px; height: 58px; border-radius: 50%; border: none; cursor: pointer;
  background: linear-gradient(135deg, #2563EB, #4F86FF); color: #fff; font-size: 26px; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 24px rgba(37, 99, 235, .45);
}
#kura-voice-root .kv-fab:focus-visible, #kura-voice-root button:focus-visible, #kura-voice-root input:focus-visible,
#kura-voice-root select:focus-visible { outline: 3px solid #93C5FD; outline-offset: 2px; }
#kura-voice-root .kv-panel {
  display: none; position: fixed; right: max(12px, calc(50vw - 198px)); bottom: 188px; z-index: 1001;
  width: 372px; max-width: calc(100vw - 24px); height: min(470px, calc(100vh - 240px)); min-height: 280px;
  flex-direction: column; background: #fff; border-radius: 22px; overflow: hidden;
  box-shadow: 0 20px 50px rgba(15, 23, 42, .30);
}
#kura-voice-root.kv-open .kv-panel { display: flex; }
#kura-voice-root .kv-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 12px 14px;
  background: linear-gradient(135deg, #2563EB, #4F86FF); color: #fff;
}
#kura-voice-root .kv-title { font-weight: 800; font-size: 1rem; }
#kura-voice-root .kv-tools { display: flex; align-items: center; gap: 6px; }
#kura-voice-root .kv-tools button, #kura-voice-root .kv-tools select {
  height: 34px; min-width: 34px; border: none; border-radius: 10px; cursor: pointer;
  background: rgba(255, 255, 255, .22); color: #fff; font-size: 15px; font-weight: 700; padding: 0 8px;
}
#kura-voice-root .kv-tools select option { color: #0F172A; }
#kura-voice-root .kv-msgs {
  flex: 1; overflow-y: auto; padding: 12px; background: #F3F7FF;
  display: flex; flex-direction: column; gap: 8px;
}
#kura-voice-root .kv-b {
  max-width: 85%; padding: 10px 13px; border-radius: 16px; font-size: .95rem; line-height: 1.4;
  white-space: pre-wrap; word-wrap: break-word; color: #0F172A;
}
#kura-voice-root .kv-b.kv-user { align-self: flex-end; background: #2563EB; color: #fff; border-bottom-right-radius: 4px; }
#kura-voice-root .kv-b.kv-assistant { align-self: flex-start; background: #fff; border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, .10); }
#kura-voice-root .kv-typing span {
  display: inline-block; width: 7px; height: 7px; margin: 0 2px; border-radius: 50%; background: #94A3B8;
  animation: kvdot 1.2s infinite ease-in-out;
}
#kura-voice-root .kv-typing span:nth-child(2) { animation-delay: .2s; }
#kura-voice-root .kv-typing span:nth-child(3) { animation-delay: .4s; }
@keyframes kvdot { 0%, 80%, 100% { opacity: .25; transform: scale(.8); } 40% { opacity: 1; transform: scale(1); } }
#kura-voice-root .kv-status { min-height: 22px; padding: 2px 14px; font-size: .8rem; color: #475569; background: #F3F7FF; }
#kura-voice-root .kv-form { display: flex; align-items: center; gap: 8px; padding: 10px; background: #fff; border-top: 1px solid #E2E8F0; }
#kura-voice-root .kv-input {
  flex: 1; min-width: 0; height: 46px; border: 1.5px solid #CBD5E1; border-radius: 23px; padding: 0 16px;
  font-size: 16px; color: #0F172A; background: #fff;
}
#kura-voice-root .kv-mic, #kura-voice-root .kv-send {
  flex: none; width: 46px; height: 46px; border-radius: 50%; border: none; cursor: pointer; font-size: 20px; color: #fff;
  background: #2563EB; display: flex; align-items: center; justify-content: center;
}
#kura-voice-root .kv-send { background: #0F172A; }
#kura-voice-root .kv-mic.kv-on { background: #DC2626; animation: kvpulse 1.2s infinite; }
@keyframes kvpulse { 0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, .55); } 100% { box-shadow: 0 0 0 14px rgba(220, 38, 38, 0); } }
@media (prefers-reduced-motion: reduce) {
  #kura-voice-root .kv-mic.kv-on, #kura-voice-root .kv-typing span { animation: none; }
}
`;

  var MARKUP = `
<button class="kv-fab" type="button">💬</button>
<section class="kv-panel" role="dialog">
  <header class="kv-head">
    <div class="kv-title">💙 <span class="kv-title-text"></span></div>
    <div class="kv-tools">
      <select class="kv-lang" aria-label="Language">
        <option value="en-US">EN</option>
        <option value="fr-CA">FR</option>
      </select>
      <button class="kv-sound" type="button">🔊</button>
      <button class="kv-close" type="button">✕</button>
    </div>
  </header>
  <div class="kv-msgs" aria-live="polite"></div>
  <div class="kv-status" aria-live="polite"></div>
  <form class="kv-form" autocomplete="off">
    <button class="kv-mic" type="button">🎙️</button>
    <input class="kv-input" type="text" enterkeyhint="send">
    <button class="kv-send" type="submit">➤</button>
  </form>
</section>
`;

  // ---------- build the widget inside the parent page ----------
  ["kura-voice-root", "kura-voice-style"].forEach(function (id) {
    var old = D.getElementById(id);
    if (old) { old.remove(); }
  });
  var style = D.createElement("style");
  style.id = "kura-voice-style";
  style.textContent = CSS;
  D.head.appendChild(style);

  var root = D.createElement("div");
  root.id = "kura-voice-root";
  root.innerHTML = MARKUP;
  D.body.appendChild(root);

  function q(sel) { return root.querySelector(sel); }
  var fab = q(".kv-fab"), panel = q(".kv-panel"), msgs = q(".kv-msgs"), statusEl = q(".kv-status");
  var form = q(".kv-form"), input = q(".kv-input"), micBtn = q(".kv-mic"), sendBtn = q(".kv-send");
  var langSel = q(".kv-lang"), soundBtn = q(".kv-sound"), closeBtn = q(".kv-close"), titleEl = q(".kv-title-text");

  // ---------- state ----------
  var history = [];          // [[role, text], ...] sent by Python
  var pending = null;        // {id, text} while we wait for the AI
  var isOpen = false;
  var listening = false;
  var voiceOn = load("kura_voice_sound") !== "0";
  var firstRender = true;
  var lastReplyId = null;
  var slowTimer = null;
  var recognition = null;

  var savedLang = load("kura_voice_lang");
  if (savedLang !== "en-US" && savedLang !== "fr-CA") {
    savedLang = String(P.navigator.language || "").toLowerCase().indexOf("fr") === 0 ? "fr-CA" : "en-US";
  }
  langSel.value = savedLang;

  function t(key) { return TEXT[langSel.value.slice(0, 2)][key]; }

  function setStatus(text) { statusEl.textContent = text || ""; }

  function applyLabels() {
    titleEl.textContent = t("title");
    input.placeholder = t("placeholder");
    fab.setAttribute("aria-label", t("open"));
    panel.setAttribute("aria-label", t("title"));
    closeBtn.setAttribute("aria-label", t("close"));
    micBtn.setAttribute("aria-label", t("mic"));
    sendBtn.setAttribute("aria-label", t("send"));
    soundBtn.textContent = voiceOn ? "🔊" : "🔇";
    soundBtn.setAttribute("aria-label", voiceOn ? t("soundOn") : t("soundOff"));
    soundBtn.title = voiceOn ? t("soundOn") : t("soundOff");
    renderMessages();
  }

  // ---------- messages ----------
  function addBubble(role, text) {
    var b = D.createElement("div");
    b.className = "kv-b " + (role === "user" ? "kv-user" : "kv-assistant");
    b.textContent = text;          // textContent: AI output is never interpreted as HTML
    msgs.appendChild(b);
  }

  function renderMessages() {
    msgs.textContent = "";
    if (history.length === 0 && !pending) { addBubble("assistant", t("hello")); }
    history.forEach(function (m) { addBubble(m[0], m[1]); });
    if (pending) {
      addBubble("user", pending.text);
      var typing = D.createElement("div");
      typing.className = "kv-b kv-assistant kv-typing";
      typing.innerHTML = "<span></span><span></span><span></span>";
      msgs.appendChild(typing);
    }
    msgs.scrollTop = msgs.scrollHeight;
  }

  // ---------- sending to Python ----------
  function submit(text, viaVoice) {
    text = (text || "").trim();
    if (!text || pending) { return; }
    stopSpeaking();
    pending = { id: uid(), text: text };
    input.value = "";
    setStatus(t("thinking"));
    renderMessages();
    post("streamlit:setComponentValue", {
      value: { id: pending.id, text: text, voice: !!viaVoice, lang: langSel.value },
      dataType: "json"
    });
    clearTimeout(slowTimer);
    slowTimer = setTimeout(function () {
      if (pending) { pending = null; setStatus(t("slow")); renderMessages(); }
    }, REPLY_TIMEOUT_MS);
  }

  // ---------- microphone (speech to text) ----------
  var SpeechRec = P.SpeechRecognition || P.webkitSpeechRecognition;

  function setListening(on) {
    listening = on;
    micBtn.classList.toggle("kv-on", on);
    micBtn.textContent = on ? "⏹" : "🎙️";
  }

  function startListening() {
    if (!SpeechRec) { setStatus(t("unsupported")); return; }
    if (listening || pending) { return; }
    stopSpeaking();

    var finalText = "";
    var failed = false;
    var rec = new SpeechRec();
    recognition = rec;
    rec.lang = langSel.value;
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    rec.onstart = function () { setListening(true); setStatus(t("listening")); };
    rec.onresult = function (e) {
      var interim = "";
      for (var i = e.resultIndex; i < e.results.length; i++) {
        var piece = e.results[i][0].transcript;
        if (e.results[i].isFinal) { finalText += piece; } else { interim += piece; }
      }
      input.value = (finalText + interim).trim();
    };
    rec.onerror = function (e) {
      failed = true;
      if (e.error === "not-allowed" || e.error === "service-not-allowed") { setStatus(t("denied")); }
      else if (e.error === "no-speech") { setStatus(t("nospeech")); }
      else if (e.error === "network") { setStatus(t("network")); }
      else if (e.error !== "aborted") { setStatus(t("nospeech")); }
    };
    rec.onend = function () {
      setListening(false);
      if (recognition === rec) { recognition = null; }
      var said = (finalText || input.value).trim();
      if (!failed && said) { submit(said, true); }
      else if (!failed) { setStatus(t("nospeech")); }
    };
    try { rec.start(); } catch (err) { setListening(false); setStatus(t("unsupported")); }
  }

  function stopListening() {
    if (recognition) { try { recognition.stop(); } catch (e) { /* ignore */ } }
  }

  // ---------- speaking (text to speech) ----------
  var synth = P.speechSynthesis;

  function pickVoice(lang) {
    if (!synth) { return null; }
    var voices = synth.getVoices() || [];
    var want = lang.toLowerCase().replace("_", "-");
    var i;
    for (i = 0; i < voices.length; i++) {
      if (voices[i].lang.toLowerCase().replace("_", "-") === want) { return voices[i]; }
    }
    for (i = 0; i < voices.length; i++) {
      if (voices[i].lang.toLowerCase().indexOf(want.slice(0, 2)) === 0) { return voices[i]; }
    }
    return null;
  }

  function stopSpeaking() { if (synth) { try { synth.cancel(); } catch (e) { /* ignore */ } } }

  function speak(text, lang) {
    if (!synth || !P.SpeechSynthesisUtterance) { return; }
    lang = lang || langSel.value;
    // no emoji or markdown symbols in the spoken text
    var clean = String(text).replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, "").replace(/[*_`#>]/g, "");
    var sentences = clean.match(/[^.!?\n]+[.!?]*/g) || [clean];
    synth.cancel();
    var voice = pickVoice(lang);
    sentences.forEach(function (s) {
      s = s.trim();
      if (!s) { return; }
      var u = new P.SpeechSynthesisUtterance(s);   // one short utterance per sentence (more reliable)
      u.lang = lang;
      u.rate = 0.95;                               // slightly slower: easier to follow
      if (voice) { u.voice = voice; }
      synth.speak(u);
    });
  }

  // ---------- open / close ----------
  function setOpen(open, fromClick) {
    isOpen = open;
    root.classList.toggle("kv-open", open);
    fab.textContent = open ? "✕" : "💬";
    fab.setAttribute("aria-label", open ? t("close") : t("open"));
    save("kura_voice_open", open ? "1" : "0");
    if (open) {
      msgs.scrollTop = msgs.scrollHeight;
      if (fromClick && AUTO_LISTEN) { startListening(); }
    } else {
      stopListening();
      stopSpeaking();
    }
  }

  // ---------- events ----------
  fab.addEventListener("click", function () { setOpen(!isOpen, true); });
  closeBtn.addEventListener("click", function () { setOpen(false, false); });
  micBtn.addEventListener("click", function () { if (listening) { stopListening(); } else { startListening(); } });
  form.addEventListener("submit", function (e) { e.preventDefault(); submit(input.value, false); });
  panel.addEventListener("keydown", function (e) { if (e.key === "Escape") { setOpen(false, false); } });
  soundBtn.addEventListener("click", function () {
    voiceOn = !voiceOn;
    save("kura_voice_sound", voiceOn ? "1" : "0");
    if (!voiceOn) { stopSpeaking(); }
    applyLabels();
  });
  langSel.addEventListener("change", function () { save("kura_voice_lang", langSel.value); applyLabels(); });

  // ---------- data coming from Python ----------
  window.addEventListener("message", function (ev) {
    var d = ev.data;
    if (ev.source !== P || !d || d.type !== "streamlit:render") { return; }
    var args = d.args || {};
    var reply = args.reply || null;
    history = args.history || [];

    if (pending && reply && reply.id === pending.id) {
      pending = null;
      clearTimeout(slowTimer);
      setStatus("");
    }
    renderMessages();

    if (reply && reply.id && reply.id !== lastReplyId) {
      lastReplyId = reply.id;
      var last = history.length ? history[history.length - 1] : null;
      // read the answer aloud only for a NEW answer to a spoken question (never when the page reloads)
      if (!firstRender && reply.speak && voiceOn && last && last[0] === "assistant") { speak(last[1], reply.lang); }
    }
    firstRender = false;
  });

  // ---------- cleanup: remove the widget when the component leaves the page (log out) ----------
  var cleaned = false;
  function cleanup() {
    if (cleaned) { return; }
    cleaned = true;
    try { if (recognition) { recognition.abort(); } } catch (e) { /* ignore */ }
    stopSpeaking();
    root.remove();
    style.remove();
  }
  window.addEventListener("pagehide", cleanup);
  window.addEventListener("unload", cleanup);

  applyLabels();
  setOpen(load("kura_voice_open") === "1", false);
})();
</script>
</body>
</html>
'''

