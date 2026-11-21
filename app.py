# app.py
import streamlit as st

# ---- TEMPORAIRE : remplacé plus tard par care_records.py (Backend 2) ----
appointments = [
    {"id": 1, "title": "Suivi diabète", "date": "2026-11-22", "time": "10:00",
     "location": "Clinique Saint-Laurent"},
    {"id": 2, "title": "Prise de sang", "date": "2026-11-28", "time": "08:30",
     "location": "CLSC Côte-des-Neiges"},
]
reminders = [
    {"id": 1, "name": "Insuline", "time": "08:00", "taken": False},
]

# ---- TEMPORAIRE : remplacé plus tard par schedule.py (Backend 1) ----
def sort_by_date(appts):
    return sorted(appts, key=lambda a: a["date"])

# ---- La vraie page (ton travail) ----
st.title("Kura")

st.header("Today")
for r in reminders:
    st.checkbox(f'{r["time"]} — {r["name"]}', key=f'rem_{r["id"]}')

st.header("Upcoming appointments")
for a in sort_by_date(appointments):
    st.write(f'**{a["title"]}** — {a["date"]} à {a["time"]}, {a["location"]}')
