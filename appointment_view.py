# Frontend 2 : page d'un rendez-vous
import streamlit as st
from datetime import date, time
from care_records import add_appointment


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


DOCTORS = [
    "Dr. Martin — Family doctor",
    "Dr. Benali — Cardiologist",
    "Dr. Nguyen — Endocrinologist",
]
HOURS = ["09:00", "10:30", "13:00", "14:30", "16:00"]


def show_add_appointment(profile):
    st.subheader("Choose a date")
    day = st.date_input("Date", min_value=date.today(), key="book_date")

    st.subheader("Available hours")
    hour = st.pills("Time", HOURS, key="book_hour")

    st.subheader("Doctor")
    doctor = st.radio("Doctor", DOCTORS, key="book_doctor")

    if st.button("Book appointment", key="book_btn"):
        if not hour:
            st.warning("Pick a time first.")
            return
        name, specialty = doctor.split(" — ")
        add_appointment(
            profile,
            f"{specialty} visit",
            day.isoformat(),
            hour,
            "Demo Health Clinic",
            name,
        )
        st.success(f"Booked with {name} on {day} at {hour} ✅")
