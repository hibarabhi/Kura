from datetime import date


def get_todays_reminders(reminders):
    today = date.today().isoformat()
    return [reminder for reminder in reminders if reminder["date"] == today]


def get_upcoming_appointments(appointments):
    today = date.today().isoformat()
    upcoming = [
        appointment
        for appointment in appointments
        if appointment["date"] >= today
    ]
    return sorted(upcoming, key=lambda item: (item["date"], item["time"]))
