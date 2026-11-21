import streamlit as st

from care_records import create_demo_profile
from appointment_view import show_ride_request, show_update_appointment
from appointment_view import show_appointment_notes, show_ride_request
from schedule import get_todays_reminders, get_upcoming_appointments 




st.title("Kura")

if "profile" not in st.session_state:
    with st.form("demo_profile"):
        name = st.text_input("First name or nickname")
        submitted = st.form_submit_button("Create demo profile")

    if submitted:
        if name.strip():
            st.session_state["profile"] = create_demo_profile(name)
            st.rerun()
        else:
            st.warning("Enter a name to get started.")

    st.stop()

profile = st.session_state["profile"]

st.subheader(f'Welcome, {profile["name"]}')

st.header("Today")
for reminder in get_todays_reminders(profile["reminders"]):
    reminder["taken"] = st.checkbox(
        f'{reminder["time"]} — {reminder["title"]}',
        value=reminder["taken"],
        key=f'rem_{reminder["id"]}',
    )

st.header("Upcoming appointments")
for appointment in get_upcoming_appointments(profile["appointments"]):
    st.write(
        f'**{appointment["title"]}** — {appointment["date"]} '
        f'at {appointment["time"]}, {appointment["location"]}'
    )
    
    show_ride_request(appointment)
    show_appointment_notes(appointment)
    show_update_appointment(appointment)
