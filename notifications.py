# notifications.py : la cloche 🔔 avec les alertes médicaments et rendez-vous  (Frontend 1)
import html
from datetime import date, datetime, timedelta

import streamlit as st


def _now():
    """Heure de Montréal (même si le serveur est ailleurs, ex. Streamlit Cloud)."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Toronto")).replace(tzinfo=None)
    except Exception:
        return datetime.now()


def get_notifications(profile):
    now = _now()
    today = now.date()
    items = []

    # 💊 médicaments d'aujourd'hui pas encore pris
    for r in sorted(profile["reminders"], key=lambda r: (r["date"], r["time"])):
        if r["date"] != today.isoformat() or r["taken"]:
            continue
        due = datetime.fromisoformat(f'{r["date"]}T{r["time"]}')
        if due <= now:
            items.append({"kind": "med", "level": "danger", "icon": "💊", "ref": r,
                          "title": f'Missed: {r["title"]}',
                          "text": f'Was due at {r["time"]} today.'})
        elif due - now <= timedelta(hours=3):
            minutes = int((due - now).total_seconds() // 60)
            items.append({"kind": "med", "level": "warn", "icon": "💊", "ref": r,
                          "title": f'Soon: {r["title"]}',
                          "text": f'Due at {r["time"]} (in {minutes} min).'})
        else:
            items.append({"kind": "med", "level": "info", "icon": "💊", "ref": r,
                          "title": f'Today: {r["title"]}',
                          "text": f'Due at {r["time"]}.'})

    # 🩺 rendez-vous dans les 2 prochains jours
    for a in sorted(profile["appointments"], key=lambda a: (a["date"], a["time"])):
        days = (date.fromisoformat(a["date"]) - today).days
        if days < 0 or days > 2:
            continue
        if days == 0 and datetime.fromisoformat(f'{a["date"]}T{a["time"]}') < now:
            continue
        when = {0: "Today", 1: "Tomorrow", 2: "In 2 days"}[days]
        doctor = a.get("doctor", "")
        items.append({"kind": "appt", "level": "warn" if days == 0 else "info", "icon": "🩺", "ref": a,
                      "title": f'{when}: {a["title"]}',
                      "text": f'{a["time"]}' + (f' · {doctor}' if doctor else "") + f' · {a["location"]}'})
    return items


def _mark_taken(reminder):
    reminder["taken"] = True
    # met aussi à jour la case à cocher de l'accueil / de la page Meds
    st.session_state[f'rem_{reminder["id"]}'] = True


def show_bell(profile, go):
    items = get_notifications(profile)

    # pastille rouge avec le nombre de notifications
    if items:
        st.markdown(f'<style>.st-key-bellbtn::after {{ content: "{min(len(items), 9)}"; }}</style>',
                    unsafe_allow_html=True)

    with st.container(key="bellbtn"):
        with st.popover("Notifications"):
            st.markdown('<div class="kn-head">🔔 Notifications</div>', unsafe_allow_html=True)
            if not items:
                st.markdown('<div class="kn-empty">You\'re all caught up ✨</div>', unsafe_allow_html=True)

            for n in items:
                st.markdown(
                    f'<div class="kn-item {n["level"]}"><div class="kn-icon">{n["icon"]}</div><div>'
                    f'<div class="kn-title">{html.escape(n["title"])}</div>'
                    f'<div class="kn-text">{html.escape(n["text"])}</div></div></div>',
                    unsafe_allow_html=True,
                )
                if n["kind"] == "med":
                    st.button("✓ Mark as taken", key=f'kn_take_{n["ref"]["id"]}',
                              on_click=_mark_taken, args=(n["ref"],))
                else:
                    st.button("🚗 Ask for a ride", key=f'kn_ride_{n["ref"]["id"]}',
                              on_click=go, args=("rides",))