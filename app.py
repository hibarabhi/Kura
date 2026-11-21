# app.py  (Frontend 1)
import streamlit as st
from style import load_css, header, hero, appointment_card
from care_records import create_demo_profile
from schedule import get_todays_reminders, get_upcoming_appointments
from appointment_view import (
    show_ride_request,
    show_appointment_notes,
    show_update_appointment,
    show_add_appointment,
)
from caregiver import show_share_code, show_link_form
# 👉 COLLE ICI la ligne "from calendar_view import ..." de l'étape 4

st.set_page_config(page_title="Kura", page_icon="💙")
load_css()

# ================= ÉCRAN DE CONNEXION =================
if "profile" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>💙 Kura</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#64748B'>"
        "Your appointments, medications and rides in one place.</p>",
        unsafe_allow_html=True,
    )
    with st.form("demo_profile"):
        name = st.text_input("First name or nickname")
        submitted = st.form_submit_button("Get started")
    if submitted:
        if name.strip():
            st.session_state["profile"] = create_demo_profile(name)
            st.rerun()
        else:
            st.warning("Enter a name to get started.")

    with st.expander("I'm a caregiver"):
        show_link_form()
    st.stop()

profile = st.session_state["profile"]

home, book, messages, me = st.tabs(["🏠 Home", "📅 Book", "💬 Messages", "👤 Profile"])

# ================= HOME =================
with home:
    header(profile["name"])

    st.subheader("Today")
    todays = get_todays_reminders(profile["reminders"])
    if not todays:
        st.caption("No reminders today.")
    for reminder in todays:
        reminder["taken"] = st.checkbox(
            f'{reminder["time"]} — {reminder["title"]}',
            value=reminder["taken"],
            key=f'rem_{reminder["id"]}',
        )

    st.subheader("Upcoming appointments")
    for appointment in get_upcoming_appointments(profile["appointments"]):
        appointment_card(appointment)
        show_ride_request(appointment)
        show_appointment_notes(appointment)
        show_update_appointment(appointment)

# ================= BOOK =================
with book:
    hero("Book Appointment", "Consult with trusted doctors anytime.")
    show_add_appointment(profile)
    # 👉 COLLE ICI la ligne qui affiche le calendrier (étape 4)

# ================= MESSAGES =================
with messages:
    st.subheader("Contact your clinic")
    if "chat" not in st.session_state:
        st.session_state.chat = [
            ("assistant", "Hi! This is Demo Health Clinic. How can we help?")
        ]
    for role, text in st.session_state.chat:
        st.chat_message(role).write(text)

    msg = st.chat_input("Type a message...")
    if msg:
        st.session_state.chat.append(("user", msg))
        st.session_state.chat.append((
            "assistant",
            "Thanks! Our team will reply soon. For an emergency, call 911.",
        ))
        st.rerun()

# ================= PROFILE =================
with me:
    st.subheader("Profile")
    st.write(f'Name: {profile["name"]}')
    show_share_code(profile)
    if st.button("Log out"):
        del st.session_state["profile"]
        st.rerun()
