import random
import string
from datetime import date, datetime


import streamlit as st




# ---------- shared storage (all browsers see the same dictionary) ----------


@st.cache_resource
def get_store():
    '''One dictionary shared by all browsers while the server is running.'''
    return {}




def create_patient_code(profile):
    store = get_store()
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "KURA-" + "".join(random.choices(chars, k=4))
        if code not in store:
            break
    # we store the profile object itself, so the caregiver sees live updates
    store[code] = {"profile": profile, "caregivers": []}
    return code




def close_patient_code(code):
    '''Called when the patient logs out: the code stops working.'''
    if code:
        get_store().pop(code, None)




def get_patient(code):
    entry = get_store().get(code)
    return entry["profile"] if entry else None




def is_linked(code, name):
    entry = get_store().get(code)
    return entry is not None and name in entry["caregivers"]




def link_caregiver(code, caregiver_name):
    store = get_store()
    code = code.strip().upper()
    name = caregiver_name.strip()


    if code not in store:
        return False, "This code does not exist."
    if not name:
        return False, "Please enter your name."
    if name in store[code]["caregivers"]:
        return False, "Someone with this name is already linked to this patient."


    store[code]["caregivers"].append(name)
    return True, f'Linked to {store[code]["profile"]["name"]}.'




def unlink_caregiver(code, name):
    entry = get_store().get(code)
    if entry and name in entry["caregivers"]:
        entry["caregivers"].remove(name)




# ---------- patient side ----------


def show_share_code(profile):
    '''Shows the patient's code and the list of linked people.'''
    code = st.session_state.get("patient_code")
    if code is None or get_patient(code) is not profile:
        code = create_patient_code(profile)
        st.session_state["patient_code"] = code


    st.subheader("Link a caregiver")
    st.write("Give this code to anyone you want to link:")
    st.code(code, language=None)


    caregivers = get_store()[code]["caregivers"]
    if not caregivers:
        st.caption("No one is linked yet.")
    for name in list(caregivers):
        col_name, col_button = st.columns([3, 1])
        col_name.write(name)
        if col_button.button("Remove", key=f"remove_{name}"):
            unlink_caregiver(code, name)
            st.rerun()




# ---------- caregiver side ----------


def show_link_form():
    '''Form where a caregiver enters the patient's code.'''
    with st.form("link_form"):
        code = st.text_input("Patient's code")
        name = st.text_input("Your name")
        submitted = st.form_submit_button("Link")


    if submitted:
        ok, message = link_caregiver(code, name)
        if ok:
            st.session_state["linked_code"] = code.strip().upper()
            st.session_state["linked_name"] = name.strip()
            st.rerun()
        else:
            st.error(message)




def is_missed(reminder):
    '''A reminder is missed if it is not taken and its time has passed.'''
    due = datetime.fromisoformat(f'{reminder["date"]}T{reminder["time"]}')
    return (not reminder["taken"]) and due < datetime.now()




@st.fragment(run_every=5)  # this section refreshes itself every 5 seconds
def show_dashboard(code):
    profile = get_patient(code)
    if profile is None:
        st.error("This patient is no longer available.")
        return


    st.subheader(f'Patient: {profile["name"]}')


    st.markdown("#### Alerts")
    missed = [r for r in profile["reminders"] if is_missed(r)]
    if missed:
        for r in missed:
            st.error(f'{r["title"]} was not taken (due {r["date"]} at {r["time"]}).')
    else:
        st.success("No alerts. Everything is on track.")


    st.markdown("#### Reminders")
    reminders = sorted(profile["reminders"], key=lambda r: (r["date"], r["time"]))
    if not reminders:
        st.caption("No reminders.")
    for r in reminders:
        if r["taken"]:
            status = "Taken"
        elif is_missed(r):
            status = "Missed"
        else:
            status = "Pending"
        st.write(f'**{r["title"]}**: {r["date"]} at {r["time"]} ({status})')


    st.markdown("#### Upcoming appointments")
    today = date.today().isoformat()
    upcoming = sorted(
        (a for a in profile["appointments"] if a["date"] >= today),
        key=lambda a: (a["date"], a["time"]),
    )
    if not upcoming:
        st.caption("No upcoming appointments.")
    for a in upcoming:
        st.write(f'**{a["title"]}**: {a["date"]} at {a["time"]}, {a["location"]}')




def show_caregiver_page():
    '''Returns True if the dashboard was shown, False if the link is not valid.'''
    code = st.session_state.get("linked_code")
    name = st.session_state.get("linked_name")


    # the patient may have removed this caregiver, logged out, or the server restarted
    if not is_linked(code, name):
        st.session_state.pop("linked_code", None)
        st.session_state.pop("linked_name", None)
        st.warning("You are no longer linked to this patient.")
        return False


    st.title("💙 Kura: Caregiver")
    show_dashboard(code)


    if st.button("Unlink myself"):
        unlink_caregiver(code, name)
        st.session_state.pop("linked_code", None)
        st.session_state.pop("linked_name", None)
        st.rerun()
    return True
