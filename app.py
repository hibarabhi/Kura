# app.py  (Frontend 1)
import streamlit as st
from style import (
    load_css, login_screen, home_header,
    section, tip_card, hero, appointment_card,
)
from care_records import create_demo_profile
from schedule import get_todays_reminders, get_upcoming_appointments
from appointment_view import (
    show_ride_request,
    show_appointment_notes,
    show_update_appointment,
    show_add_appointment,
)
from caregiver import (
    show_share_code,
    show_link_form,
    show_caregiver_page,
    close_patient_code,
)
from calendar_view import show_week_calendar
from ai_chat import get_ai_reply

st.set_page_config(page_title="Kura", page_icon="💙")
load_css()

# ================= PAGE PROCHE AIDANT =================
if "linked_code" in st.session_state:
    if show_caregiver_page():
        st.stop()

# ================= LOGIN =================
if "profile" not in st.session_state:
    # Le formulaire HTML renvoie le nom dans l'adresse : ?user=Sam
    user = st.query_params.get("user", "").strip()
    if user:
        st.query_params.clear()
        st.session_state["profile"] = create_demo_profile(user.split("@")[0])
        st.session_state["page"] = "home"
        st.rerun()

    login_screen()
    with st.expander("🤝  I'm a caregiver"):
        show_link_form()
    st.stop()

profile = st.session_state["profile"]

# ================= NAVIGATION =================
# La page affichée est gardée dans st.session_state["page"].
# Chaque bouton (services, Book Now, barre du bas) change cette valeur.
if "page" not in st.session_state:
    st.session_state["page"] = "home"


def go(target):
    st.session_state["page"] = target


def back_button():
    with st.container(key="back"):
        st.button("←  Back", key=f'back_{st.session_state["page"]}', on_click=go, args=("home",))


# (icône, nom, page ouverte au clic)
SERVICES = [
    ("🚗", "Rides", "rides"),
    ("💊",