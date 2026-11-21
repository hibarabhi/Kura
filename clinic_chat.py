# clinic_chat.py : réponses automatiques par mots-clés
import re
from schedule import get_upcoming_appointments

# (mots-clés, réponse). L'ordre compte : la première règle trouvée gagne.
RULES = [
    (["emergency", "urgence", "urgent", "911", "chest", "breathe", "poitrine", "respirer"],
     "🚨 If this is an emergency, call 911 right now."),

    (["pain", "sick", "fever", "hurt", "douleur", "malade", "fièvre", "mal"],
     "I can't give medical advice here. For a health question that isn't urgent, "
     "call Info-Santé at 811. For an emergency, call 911."),

    (["cancel", "reschedule", "change", "move", "annuler", "déplacer", "changer"],
     "To cancel or reschedule, call us at 514-555-0123. Once we confirm, "
     "update the date in the Home tab under 'Update appointment'."),

    (["appointment", "appointments", "next", "when", "rendez", "prochain", "quand"],
     "NEXT_APPOINTMENT"),  # réponse spéciale, calculée plus bas

    (["ride", "drive", "lift", "transport", "trajet"],
     "Need a ride? Open your appointment in the Home tab and tap 'Ask for a ride'. "
     "You choose exactly which details to share."),

    (["medication", "medicine", "insulin", "pill", "médicament", "insuline"],
     "Your medication reminders are in the Home tab under 'Today'. "
     "For questions about your dose, please ask your doctor or pharmacist."),

    (["hours", "open", "close", "horaires", "ouvert", "fermé"],
     "Demo Health Clinic is open Monday to Friday, 8:00 to 17:00."),

    (["where", "address", "location", "adresse", "où"],
     "The clinic address is shown on each appointment card in the Home tab."),

    (["thanks", "thank", "merci"],
     "You're welcome! Take care 💙"),

    (["hello", "hi", "hey", "bonjour", "salut", "allo"],
     "Hello! 👋 You can ask me about your appointments, rides, "
     "medications or our opening hours."),
]

DEFAULT = "Thanks for your message! Our team will reply soon. For an emergency, call 911."


def get_reply(message, profile):
    # On découpe le message en mots, en minuscules
    words = set(re.findall(r"[a-zàâçéèêëîïôûùüÿ0-9']+", message.lower()))

    for keywords, reply in RULES:
        if words & set(keywords):          # au moins un mot-clé dans le message ?
            if reply == "NEXT_APPOINTMENT":
                return next_appointment_reply(profile)
            return reply

    return DEFAULT


def next_appointment_reply(profile):
    upcoming = get_upcoming_appointments(profile["appointments"])
    if not upcoming:
        return "You have no upcoming appointments. You can book one in the Book tab."
    a = upcoming[0]
    return (f'Your next appointment is "{a["title"]}" on {a["date"]} '
            f'at {a["time"]}, at {a["location"]}.')