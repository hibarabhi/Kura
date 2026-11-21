from datetime import date, timedelta


def create_demo_profile(name):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    return {
        "name": name.strip(),
        "appointments": [
            {
                "id": 1,
                "title": "Follow-up appointment",
                "date": tomorrow.isoformat(),
                "time": "10:00",
                "location": "Demo Health Clinic",
                "notes": "",
            },
            {
                "id": 2,
                "title": "Blood test",
                "date": (today + timedelta(days=3)).isoformat(),
                "time": "08:30",
                "location": "Demo Health Clinic",
                "notes": "",
            }
        ],
        "reminders": [
            {
                "id": 1,
                "title": "Morning medication",
                "date": today.isoformat(),
                "time": "08:00",
                "taken": False,
            }
        ],
    }


def add_appointment(profile, title, appointment_date, appointment_time, location):
    appointments = profile["appointments"]
    next_id = max((appointment["id"] for appointment in appointments), default=0) + 1

    appointments.append({
        "id": next_id,
        "title": title.strip(),
        "date": appointment_date,
        "time": appointment_time,

        "location": location.strip(),
        "notes": "",
    })
