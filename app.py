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
from kura_assistant import show_assistant, reset_assistant
from meds import (
    show_add_medication, show_medication_list,
    show_prescriptions, show_prescription_list,
)

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
    (":material/directions_car:", "Rides", "rides"),
    (":material/medication:", "Meds", "meds"),
    (":material/diversity_1:", "Caregiver", "profile"),
    (":material/calendar_month:", "Book", "book"),
]

# (page, icône, nom) pour la barre du bas
NAV = [
    ("home", ":material/home:", "Home"),
    ("book", ":material/stethoscope:", "Book"),
    ("meds", ":material/medication:", "Meds"),
    ("profile", ":material/person:", "Profile"),
]

if st.session_state["page"] not in {"home", "rides", "meds", "book", "profile"}:
    st.session_state["page"] = "home"
page = st.session_state["page"]

# ================= HOME =================
if page == "home":
    home_header(profile["name"])
    search = st.text_input(
        "Search",
        placeholder="🔍  Search doctors or appointments...",
        label_visibility="collapsed",
        key="home_search",
    )

    with st.container(key="hero"):
        st.markdown(
            '<div class="kura-hero-title">Book Appointment</div>'
            '<div class="kura-hero-text">Consult with trusted doctors anytime.</div>',
            unsafe_allow_html=True,
        )
        st.button("Book Now  →", key="book_now", on_click=go, args=("book",))

    section("Our services")
    with st.container(key="services"):
        cols = st.columns(4)
        for col, (icon, label, target) in zip(cols, SERVICES):
            with col:
                st.button(label, icon=icon, key=f"svc_{label}", on_click=go, args=(target,))

    section("Today")
    todays = get_todays_reminders(profile["reminders"])
    if not todays:
        st.caption("No reminders today.")
    for reminder in todays:
        reminder["taken"] = st.checkbox(
            f'💊  {reminder["time"]} — {reminder["title"]}',
            value=reminder["taken"],
            key=f'rem_{reminder["id"]}',
        )

    section("Upcoming appointments")
    query = search.strip().lower()
    shown = 0
    for appointment in get_upcoming_appointments(profile["appointments"]):
        text = f'{appointment["title"]} {appointment.get("doctor", "")}'.lower()
        if query and query not in text:
            continue
        shown += 1
        appointment_card(appointment)
        show_ride_request(appointment)
        show_appointment_notes(appointment)
        show_update_appointment(appointment)
    if shown == 0:
        st.caption("No appointments found.")

    tip_card()

# ================= RIDES (service) =================
elif page == "rides":
    back_button()
    hero("Ask for a ride", "Pick an appointment and choose what to share.")
    upcoming = get_upcoming_appointments(profile["appointments"])
    if not upcoming:
        st.caption("No upcoming appointments.")
    for appointment in upcoming:
        appointment_card(appointment)
        show_ride_request(appointment)

# ================= MEDICATION (service) =================
elif page == "meds":
    back_button()
    hero("Medication", "Add your medications and tick them once taken.", icon="💊")
    show_add_medication(profile)
    show_prescriptions(profile)
    med_query = st.text_input(
        "Search medications",
        placeholder="🔍  Search your medications...",
        label_visibility="collapsed",
        key="med_search",
    )
    show_medication_list(profile, med_query.strip().lower(), section)
    show_prescription_list(profile, med_query.strip().lower(), section)
    st.caption("Questions about your dose? Ask your doctor or pharmacist.")

# ================= BOOK =================
elif page == "book":
    hero("Book Appointment", "Pick a date, a time and a doctor.")
    show_add_appointment(profile)
    upcoming = get_upcoming_appointments(profile["appointments"])
    show_week_calendar(upcoming)

# ================= PROFILE =================
elif page == "profile":
    section("Profile")
    st.write(f'Name: {profile["name"]}')
    show_share_code(profile)
    if st.button("Log out"):
        close_patient_code(st.session_state.get("patient_code"))
        st.session_state.pop("patient_code", None)
        reset_assistant()
        st.session_state["page"] = "home"
        del st.session_state["profile"]
        st.rerun()

# ================= BARRE DU BAS =================
with st.container(key="nav"):
    cols = st.columns(len(NAV))
    for col, (target, icon, label) in zip(cols, NAV):
        with col:
            st.button(
                label,
                icon=icon,
                key=f"nav_{target}",
                on_click=go,
                args=(target,),
                type="primary" if page == target else "secondary",
            )

# ================= ASSISTANT IA (bulle flottante : micro + texte) =================
show_assistant(profile)