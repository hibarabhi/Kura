# profile_view.py : page "Mon profil" (photo + infos personnelles)  (Frontend 1)
import base64
import html
import io
from datetime import date

import streamlit as st


def _square_thumbnail(file_bytes):
    """Recadre la photo en carré 256x256 (plus légère). Renvoie du base64 JPEG."""
    try:
        from PIL import Image   # installé avec Streamlit
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        side = min(img.size)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((256, 256))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85)
        return base64.b64encode(out.getvalue()).decode()
    except Exception:
        return base64.b64encode(file_bytes).decode()


def avatar_button_css(profile):
    """Si une photo existe, le rond en haut de l'accueil affiche la photo."""
    if not profile.get("photo"):
        return
    st.markdown(
        '<style>.st-key-avatarbtn .stButton button {'
        f'background: url(data:image/jpeg;base64,{profile["photo"]}) center / cover no-repeat !important;}}'
        '.st-key-avatarbtn .stButton button p { visibility: hidden; }</style>',
        unsafe_allow_html=True,
    )


def _avatar_html(profile):
    if profile.get("photo"):
        return f'<img class="kp-avatar" src="data:image/jpeg;base64,{profile["photo"]}" alt="photo">'
    initial = html.escape(profile["name"].strip()[:1].upper() or "?")
    return f'<div class="kp-avatar">{initial}</div>'


def _row(icon, label, value):
    if not value:
        return ""
    return (f'<div class="kp-row"><b>{icon}</b><div><span>{label}</span>'
            f'{html.escape(str(value))}</div></div>')


def show_profile(profile):
    info = profile.setdefault("info", {})

    # ---------- carte du profil ----------
    birthday = info.get("birthday")
    rows = "".join([
        _row("📞", "Phone", info.get("phone")),
        _row("✉️", "Email", info.get("email")),
        _row("🎂", "Date of birth", date.fromisoformat(birthday).strftime("%d %B %Y") if birthday else ""),
        _row("🏠", "Address", info.get("address")),
        _row("🆘", "Emergency contact",
             " · ".join(x for x in (info.get("ec_name"), info.get("ec_phone")) if x)),
        _row("⚠️", "Allergies", info.get("allergies")),
        _row("📝", "Notes for my care team", info.get("notes")),
    ])
    if not rows:
        rows = '<div class="kp-empty">Add your information below so your care team and caregivers can reach you.</div>'
    st.markdown(
        f'<div class="kp-card">{_avatar_html(profile)}'
        f'<div class="kp-name">{html.escape(profile["name"])}</div>'
        f'<div class="kp-sub">Kura patient</div>'
        f'<div class="kp-rows">{rows}</div></div>',
        unsafe_allow_html=True,
    )

    # ---------- modifier ----------
    with st.expander("✏️  Edit my profile", expanded=not info):
        with st.form("profile_form"):
            photo = st.file_uploader("Profile photo", type=["png", "jpg", "jpeg"])
            name = st.text_input("First name", value=profile["name"])
            col1, col2 = st.columns(2)
            phone = col1.text_input("Phone", value=info.get("phone", ""))
            email = col2.text_input("Email", value=info.get("email", ""))
            dob = st.date_input(
                "Date of birth",
                value=date.fromisoformat(birthday) if birthday else None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                format="YYYY-MM-DD",
            )
            address = st.text_input("Address", value=info.get("address", ""))
            st.markdown("**Emergency contact**")
            col3, col4 = st.columns(2)
            ec_name = col3.text_input("Name", value=info.get("ec_name", ""))
            ec_phone = col4.text_input("Phone ", value=info.get("ec_phone", ""))
            allergies = st.text_input("Allergies (optional)", value=info.get("allergies", ""))
            notes = st.text_area("Notes for my care team (optional)", value=info.get("notes", ""))
            saved = st.form_submit_button("Save profile")

        if saved:
            if name.strip():
                profile["name"] = name.strip()
            info.update({
                "phone": phone.strip(), "email": email.strip(),
                "birthday": dob.isoformat() if dob else "",
                "address": address.strip(),
                "ec_name": ec_name.strip(), "ec_phone": ec_phone.strip(),
                "allergies": allergies.strip(), "notes": notes.strip(),
            })
            if photo is not None:
                profile["photo"] = _square_thumbnail(photo.getvalue())
            st.rerun()

        st.caption("Demo: your information is only kept while the app is running.")

    if profile.get("photo") and st.button("Remove photo", key="remove_photo"):
        profile.pop("photo", None)
        st.rerun()