# Frontend 2 : page d'un rendez-vous
import streamlit as st
from datetime import date, time


def show_ride_request(appointment):
    '''
    Show a copyable ride request with only the appointment details selected.

    The appointment dictionary provides the ID, date, time, and location.
    If no details are selected, display a prompt to choose at least one.
    '''
    with st.expander("Ask for a ride"): # puts the indented widgets inside a section the patient can open and close
        details = st.multiselect(
            "Choose what to share",
            ["Date", "Time", "Location"],
            key=f'ride_details_{appointment["id"]}',
        ) # Display 3 choices, and gives back a list of the selected choices

        if not details: # if the patient selected nothing
            st.caption("Select at least one detail to preview your message.")
            return # exits the function

        lines = ["Hi! Could you give me a ride to an appointment?"]

        # Adds to the list 'lines' the infos that the patient wants to share about his appointment
        if "Date" in details:
            lines.append(f'Date: {appointment["date"]}')
        if "Time" in details:
            lines.append(f'Time: {appointment["time"]}')
        if "Location" in details:
            lines.append(f'Location: {appointment["location"]}')

        st.code("\n".join(lines), language=None)


def show_appointment_notes(appointment):
    '''
    Lets the patient write or edit a note for one appointment.
    Reads the old note to fill the text box, then saves the new one when the patient clicks Save notes.
    '''
    with st.expander("Appointment notes"):
        # Section containing a form that groups the text box and the save button
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
    '''
    
    '''
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
            st.rerun()# Frontend 2 : page d'un rendez-vous
