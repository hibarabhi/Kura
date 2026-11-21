# meds.py : ajouter et chercher des médicaments  (Frontend 1)
import html
import re
from datetime import date, time, timedelta
from itertools import groupby

import streamlit as st


def add_medication(profile, name, dose, time_str, start, days):
    """Ajoute un rappel par jour pendant `days` jours dans profile["reminders"]."""
    next_id = max((r["id"] for r in profile["reminders"]), default=0) + 1
    title = f"{name} · {dose}" if dose else name
    for i in range(days):
        profile["reminders"].append({
            "id": next_id + i,
            "title": title,
            "date": (start + timedelta(days=i)).isoformat(),
            "time": time_str,
            "taken": False,
        })


def show_add_medication(profile):
    """Formulaire pour ajouter un médicament."""
    with st.expander("➕  Add a medication"):
        with st.form("add_med", clear_on_submit=True):
            name = st.text_input("Medication name", placeholder="e.g. Vitamin D")
            dose = st.text_input("Dose (as written on your prescription)", placeholder="e.g. 1 tablet")
            col_time, col_start = st.columns(2)
            when = col_time.time_input("Time", value=time(8, 0))
            start = col_start.date_input("Start date", value=date.today())
            days = st.number_input("Repeat every day for how many days?",
                                   min_value=1, max_value=60, value=7)
            submitted = st.form_submit_button("Add medication")

        if submitted:
            if not name.strip():
                st.warning("Enter the medication name.")
                return
            add_medication(profile, name.strip(), dose.strip(),
                           when.strftime("%H:%M"), start, int(days))
            st.success(f"{name.strip()} added for {int(days)} day(s) ✅")


def _day_label(day_iso):
    today = date.today()
    if day_iso == today.isoformat():
        return "Today"
    if day_iso == (today + timedelta(days=1)).isoformat():
        return "Tomorrow"
    return date.fromisoformat(day_iso).strftime("%A %d %B")


def show_medication_list(profile, query, section):
    """Liste des rappels à venir, groupés par jour, filtrés par la recherche."""
    today = date.today().isoformat()
    reminders = sorted(profile["reminders"], key=lambda r: (r["date"], r["time"]))
    if query:
        reminders = [r for r in reminders if query in r["title"].lower()]

    upcoming = [r for r in reminders if r["date"] >= today]
    past = [r for r in reminders if r["date"] < today]

    if not upcoming:
        st.caption("No medication found." if query else "No upcoming reminders. Add one above.")

    for day, items in groupby(upcoming, key=lambda r: r["date"]):
        section(_day_label(day))
        for r in items:
            r["taken"] = st.checkbox(
                f'💊  {r["time"]} — {r["title"]}',
                value=r["taken"],
                key=f'rem_{r["id"]}',
            )

    if past:
        with st.expander(f"History ({len(past)})"):
            for r in reversed(past):
                status = "✅ Taken" if r["taken"] else "❌ Missed"
                st.write(f'{r["date"]} · {r["time"]} — {r["title"]}  ({status})')


# ---------------- Ordonnances + infos du médecin et du pharmacien ----------------


def _tel_link(phone):
    digits = re.sub(r"[^\d+]", "", phone)
    return f'<a href="tel:{digits}">{html.escape(phone)}</a>' if digits else html.escape(phone)


def show_prescriptions(profile):
    """Formulaire : téléverser une ordonnance + infos du médecin et de la pharmacie."""
    profile.setdefault("prescriptions", [])
    with st.expander("📄  Upload a prescription"):
        with st.form("add_rx", clear_on_submit=True):
            file = st.file_uploader("Prescription (photo or PDF)",
                                    type=["png", "jpg", "jpeg", "pdf"])
            medication = st.text_input("Medication(s)", placeholder="e.g. Vitamin D")

            st.markdown("**Prescribing doctor**")
            col1, col2 = st.columns(2)
            doctor = col1.text_input("Doctor's name", placeholder="Dr. Martin")
            doctor_phone = col2.text_input("Doctor's phone", placeholder="514-555-0123")

            st.markdown("**Pharmacy**")
            col3, col4 = st.columns(2)
            pharmacy = col3.text_input("Pharmacy / pharmacist", placeholder="Demo Pharmacy")
            pharmacy_phone = col4.text_input("Pharmacy phone", placeholder="514-555-0199")

            notes = st.text_area("Other info",
                                 placeholder="Refills left, instructions written by your doctor...")
            submitted = st.form_submit_button("Save prescription")

        if submitted:
            if file is None and not medication.strip():
                st.warning("Add a file or at least the medication name.")
                return
            new_id = max((p["id"] for p in profile["prescriptions"]), default=0) + 1
            profile["prescriptions"].append({
                "id": new_id,
                "file_name": file.name if file else None,
                "file_type": file.type if file else None,
                "file_bytes": file.getvalue() if file else None,
                "medication": medication.strip(),
                "doctor": doctor.strip(),
                "doctor_phone": doctor_phone.strip(),
                "pharmacy": pharmacy.strip(),
                "pharmacy_phone": pharmacy_phone.strip(),
                "notes": notes.strip(),
                "added": date.today().isoformat(),
            })
            st.success("Prescription saved ✅")

        st.caption("Demo: files are only kept while the app is running. "
                   "Use a sample prescription, not a real one.")


def show_prescription_list(profile, query, section):
    """Affiche les ordonnances enregistrées (filtrées par la recherche)."""
    prescriptions = profile.get("prescriptions", [])
    if query:
        prescriptions = [
            p for p in prescriptions
            if query in f'{p["medication"]} {p["doctor"]} {p["pharmacy"]}'.lower()
        ]
    if not prescriptions:
        return

    section("My prescriptions")
    for p in reversed(prescriptions):
        with st.container(border=True):
            title = p["medication"] or p["file_name"] or "Prescription"
            st.markdown(f"**📄 {html.escape(title)}**")
            st.caption(f'Added {p["added"]}')

            lines = []
            if p["doctor"] or p["doctor_phone"]:
                lines.append(f'🩺 {html.escape(p["doctor"] or "Doctor")}'
                             + (f' · 📞 {_tel_link(p["doctor_phone"])}' if p["doctor_phone"] else ""))
            if p["pharmacy"] or p["pharmacy_phone"]:
                lines.append(f'🏪 {html.escape(p["pharmacy"] or "Pharmacy")}'
                             + (f' · 📞 {_tel_link(p["pharmacy_phone"])}' if p["pharmacy_phone"] else ""))
            if p["notes"]:
                lines.append(f'📝 {html.escape(p["notes"])}')
            if lines:
                st.markdown("<br>".join(lines), unsafe_allow_html=True)

            if p["file_bytes"]:
                if p["file_type"] and p["file_type"].startswith("image/"):
                    with st.expander("View prescription"):
                        st.image(p["file_bytes"])
                st.download_button("⬇ Download file", p["file_bytes"],
                                   file_name=p["file_name"], key=f'rx_dl_{p["id"]}')

            if st.button("Delete", key=f'rx_del_{p["id"]}'):
                profile["prescriptions"] = [x for x in profile["prescriptions"] if x["id"] != p["id"]]
                st.rerun()
                
