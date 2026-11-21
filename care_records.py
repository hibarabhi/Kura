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
