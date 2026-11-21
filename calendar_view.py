from datetime import date, timedelta

import streamlit as st


def show_week_calendar(appointments):
    with st.expander("Appointment calendar", expanded=True):
        start_date = st.date_input(
            "First day to display",
            value=date.today(),
            min_value=date.today(),
            key="calendar_start_date",
        )

        rows = []
        for offset in range(7):
            day = start_date + timedelta(days=offset)
            visits = []

            for appointment in appointments:
                if appointment["date"] == day.isoformat():
                    visits.append(f'{appointment["time"]} — {appointment["title"]}')

            rows.append({
                "Day": day.strftime("%a, %b %d"),
                "Appointments": " | ".join(visits) if visits else "—",
            })

        st.table(rows)
        
