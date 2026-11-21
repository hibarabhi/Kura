# style.py : le design de Kura (HTML + CSS)
import html
import streamlit as st

CSS = """
<style>
.stApp { background: linear-gradient(180deg, #EAF1FF 0%, #F8FAFF 100%); }
.block-container { max-width: 520px; padding-top: 2rem; }

.kura-greeting { color: #64748B; font-size: 1rem; margin: 0; }
.kura-title { font-size: 2.1rem; font-weight: 700; line-height: 1.2;
              color: #0F172A; margin: 0 0 1.2rem; }
.kura-title span { color: #2563EB; }

.kura-hero { background: linear-gradient(135deg, #3B82F6, #1D4ED8);
             border-radius: 22px; padding: 22px; margin: 8px 0 20px;
             box-shadow: 0 10px 25px rgba(37, 99, 235, .25); }
.kura-hero h3 { color: white; margin: 0 0 4px; }
.kura-hero p  { color: #DBEAFE; margin: 0; }

.kura-card { background: white; border-radius: 18px; padding: 16px;
             display: flex; gap: 14px; align-items: center; margin: 14px 0 8px;
             box-shadow: 0 4px 14px rgba(15, 23, 42, .07); }
.kura-avatar { width: 52px; height: 52px; border-radius: 50%; flex-shrink: 0;
               background: #DBEAFE; display: flex; align-items: center;
               justify-content: center; font-size: 26px; }
.kura-name { font-weight: 600; color: #0F172A; }
.kura-meta { color: #64748B; font-size: .9rem; }
.kura-badge { margin-left: auto; background: #2563EB; color: white;
              border-radius: 999px; padding: 3px 12px; font-size: .75rem; }

[data-testid="stExpander"] { background: white; border: none; border-radius: 14px;
                             box-shadow: 0 2px 8px rgba(15, 23, 42, .05); }
.stButton button, .stFormSubmitButton button {
    background: #2563EB; color: white; border: none; border-radius: 12px; }
.stTabs [data-baseweb="tab-list"] { background: white; border-radius: 16px;
    padding: 6px; box-shadow: 0 4px 14px rgba(15, 23, 42, .07); }
</style>
"""


def load_css():
    st.markdown(CSS, unsafe_allow_html=True)


def header(name):
    name = html.escape(name)
    st.markdown(
        f'<p class="kura-greeting">Good morning, {name} 👋</p>'
        f'<p class="kura-title">Take care of<br>your <span>health.</span></p>',
        unsafe_allow_html=True,
    )


def hero(title, text):
    st.markdown(
        f'<div class="kura-hero"><h3>{title}</h3><p>{text}</p></div>',
        unsafe_allow_html=True,
    )


def appointment_card(a):
    doctor = html.escape(a.get("doctor", "Your clinic"))
    title = html.escape(a["title"])
    st.markdown(
        f'''<div class="kura-card">
              <div class="kura-avatar">🩺</div>
              <div>
                <div class="kura-name">{doctor}</div>
                <div class="kura-meta">{title}</div>
                <div class="kura-meta">📅 {a["date"]} &nbsp; 🕒 {a["time"]}</div>
              </div>
              <span class="kura-badge">Confirmed</span>
            </div>''',
        unsafe_allow_html=True,
    )