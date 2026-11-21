import random
import string
import streamlit as st


@st.cache_resource
def get_store():
    '''One dictionary shared by all users while the app is running.'''
    return {}


def create_patient_code(profile):
    store = get_store()
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "KURA-" + "".join(random.choices(chars, k=4))
        if code not in store:
            break
    # we store the profile itself so the caregiver side can read it later
    store[code] = {"profile": profile, "caregivers": []}
    return code


def link_caregiver(code, caregiver_name):
    store = get_store()
    code = code.strip().upper()
    name = caregiver_name.strip()

    if code not in store:
        return False, "This code does not exist."
    if not name:
        return False, "Please enter your name."
    if name in store[code]["caregivers"]:
        return False, "You are already linked to this patient."

    store[code]["caregivers"].append(name)
    return True, f'Linked to {store[code]["profile"]["name"]}.'


def unlink_caregiver(code, name):
    get_store()[code]["caregivers"].remove(name)


def show_share_code(profile):
    '''Patient side: shows the code and the list of linked people.'''
    if "patient_code" not in st.session_state:
        st.session_state.patient_code = create_patient_code(profile)
    code = st.session_state.patient_code

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


def show_link_form():
    '''Caregiver side: enter a code to link with a patient.'''
    with st.form("link_form"):
        code = st.text_input("Patient's code")
        name = st.text_input("Your name")
        submitted = st.form_submit_button("Link")

    if submitted:
        ok, message = link_caregiver(code, name)
        if ok:
            st.session_state.linked_code = code.strip().upper()
            st.success(message)
        else:
            st.error(message)
