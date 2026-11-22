# 💙 Kura

**Care · Cure · Connect.** Kura is a patient companion app that makes it easier to get to appointments, stay on top of medications, and keep loved ones in the loop.

Built in 30 hours at **CodeJam16** by a team of four.

🔗 **Live demo:** (https://kura-health.streamlit.app/)

---

## The problem

Getting care isn't only about finding a doctor. Many patients, especially older adults and people with chronic conditions, miss appointments because they have no ride, forget a medication dose, or juggle papers from several clinics. The people who help them (family, friends, caregivers) often don't know what's coming up.

## Our solution

Kura puts appointments, medications and the people who help you in one simple, phone-style app, with privacy controlled by the patient.

> **Demo story:** Sam has a follow-up tomorrow and no way to get there. Sam opens the appointment, taps **Ask for a ride**, picks which details to share (time and location, but not the reason for the visit) and sends the message to a friend. Meanwhile, Sam's daughter, linked as a caregiver, sees live on her own phone that the morning medication was taken.

## Features

| | Feature | What it does |
|---|---|---|
| 🚗 | **Ask for a ride** | Choose exactly which appointment details to share, preview the message, then copy it or send it by SMS. |
| 📅 | **Appointments** | Upcoming visits sorted by date, a weekly calendar, notes after each visit, and rescheduling with the clinic's phone number and a short call script. |
| 🩺 | **Book an appointment** | Pick a date, an available time and a doctor (demo data). |
| 💊 | **Medications** | Add medications with a daily schedule, tick doses as taken, search your list and see your history. |
| 📄 | **Prescriptions** | Upload a photo or PDF of a prescription with the prescribing doctor's and the pharmacy's contact info (tap to call). |
| 🔔 | **Notifications** | Missed doses, doses due soon and appointments in the next two days, with one-tap "Mark as taken" and "Ask for a ride". |
| 🤝 | **Caregiver link** | The patient shares a one-time code (KURA-XXXX). The caregiver gets a live dashboard with missed-dose alerts. The patient can remove access at any time. |
| 🎙️ | **AI voice assistant** | A floating assistant you can talk or type to. It knows your upcoming appointments and today's reminders and answers in your language. |
| 👤 | **Profile** | Profile photo, contact info, emergency contact, allergies and notes for the care team. |
| 🌙 | **Dark mode** | From the login screen or the profile page. |

## Safety and privacy

- **No medical advice.** The assistant never diagnoses, suggests medications or changes doses. It points to the patient's doctor, pharmacist or Info-Santé 811.
- **Emergencies first.** Messages that mention an emergency get an immediate "call 911" answer, before any AI is involved.
- **The patient decides what is shared.** Ride requests only include the details the patient selects, and caregivers can be unlinked at any time.
- **Demo only.** All data lives in memory while the app runs. Nothing is stored in a database. Please don't enter real health information. When the AI assistant is used, the question and the patient's demo appointments are sent to the Gemini API to generate an answer.
- **Keys stay secret.** API keys live in `.streamlit/secrets.toml`, which is excluded from Git.

## Tech stack

- **Python** and **[Streamlit](https://streamlit.io)** for the whole app
- **Custom HTML/CSS** for the phone-style design (login screen, cards, bottom navigation)
- **Google Gemini API** (free tier) for the voice and text assistant, with a keyword-based fallback when the AI is unavailable
- **Streamlit Community Cloud** for hosting

## Run it locally

```bash
git clone https://github.com/<your-username>/Kura.git
cd Kura
pip install -r requirements.txt
streamlit run app.py
```

### Optional: enable the AI assistant

1. Get a free API key at [aistudio.google.com](https://aistudio.google.com).
2. Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
3. Restart the app.

Without a key, the assistant still answers common questions using keywords.

## Project structure

```
Kura/
├── app.py               # main app: login, navigation, pages
├── style.py             # design (CSS, login screen, cards, header)
├── care_records.py      # demo patient data, adding appointments
├── schedule.py          # sorting and filtering appointments and reminders
├── appointment_view.py  # ride request, notes, rescheduling, booking
├── calendar_view.py     # weekly calendar
├── caregiver.py         # caregiver codes and live dashboard
├── meds.py              # medications and prescriptions
├── notifications.py     # notification bell
├── profile_view.py      # profile page and photo
├── kura_assistant.py    # floating AI assistant (voice + text)
├── clinic_chat.py       # keyword answers (fallback)
├── assets/              # logo and images
├── .streamlit/
│   └── config.toml      # theme
└── requirements.txt
```

## Team

| Name | Role |
|---|---|
| Arwa Azriga | Frontend: main app, design |
| Hiba Rabhi | Frontend: appointment views, booking |
| Ikram El khattab| Backend: scheduling, caregiver link, chatbot |
| Farah Daami | Backend: patient data, calendar |

## What's next

- Real accounts and secure, encrypted storage
- Push notifications on the phone for medication reminders
- Booking connected to real clinic schedules
- Ride requests sent directly to a trusted contact or a transport service
- French version of the interface

## Credits

- App logo found on Pinterest by our team
- Fonts: [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) and [Poppins](https://fonts.google.com/specimen/Poppins) (Google Fonts, Open Font License)
- AI assistant powered by the [Google Gemini API](https://ai.google.dev)

*Kura is a hackathon prototype, not a medical device.*
