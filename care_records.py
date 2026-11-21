# Frontend 2 : page d'un rendez-vous
import streamlit as st
from datetime import date, time
from care_records import add_appointment

def add_appointment(profile, title, date, time, location, doctor=""):
    new_id = max((a["id"] for a in profile["appointments"]), default=0) + 1
    appointment = {
        "id": new_id,
        "title": title,
        "date": date,
        "time": time,
        "location": location,
        "doctor": doctor,
        "notes": "",
    }
    profile["appointments"].append(appointment)
    return appointment


def show_ride_request(appointment):
    with st.expander("Ask for a ride"):
        details = st.multiselect(
            "Choose what to share",
            ["Date", "Time", "Location"],
            key=f'ride_details_{appointment["id"]}',
        )

        if not details:
            st.caption("Select at least one detail to preview your message.")
            return

        lines = ["Hi! Could you give me a ride to an appointment?"]

        if "Date" in details:
            lines.append(f'Date: {appointment["date"]}')
        if "Time" in details:
            lines.append(f'Time: {appointment["time"]}')
        if "Location" in details:
            lines.append(f'Location: {appointment["location"]}')

        st.code("\n".join(lines), language=None)


def show_appointment_notes(appointment):
    with st.expander("Appointment notes"):
        with st.form(f'notes_form_{appointment["id"]}'):
            notes = st.text_area(
                "What would you like to remember?",
                value=appointment.get("notes", ""),
            )
            saved = st.form_submit_button("Save notes")

        if saved:
            appointment["notes"] = notes
            st.success("Notes saved for this session.")


def show_update_appointment(appointment):
    with st.expander("Update appointment"):
        st.caption("Enter the new date and time confirmed by your clinic.")

        with st.form(f'update_appointment_{appointment["id"]}'):
            new_date = st.date_input(
                "New date",
                value=date.fromisoformat(appointment["date"]),
            )
            new_time = st.time_input(
                "New time",
                value=time.fromisoformat(appointment["time"]),
            )
            saved = st.form_submit_button("Save changes")

        if saved:
            appointment["date"] = new_date.isoformat()
            appointment["time"] = new_time.strftime("%H:%M")
            st.rerun()


def show_add_appointment(profile):
    with st.expander("Add appointment"):
        with st.form("add_appointment"):
            title = st.text_input("Appointment title")
            appointment_date = st.date_input("Date", min_value=date.today())
            appointment_time = st.time_input("Time", value=time(9, 0))
            location = st.text_input("Location")
            submitted = st.form_submit_button("Add appointment")

        if submitted:
            if not title.strip() or not location.strip():
                st.warning("Enter a title and location.")
                return

            add_appointment(
                profile,
                title,
                appointment_date.isoformat(),
                appointment_time.strftime("%H:%M"),
                location,
            )
            st.success("Appointment added.")
            
