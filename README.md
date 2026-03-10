#  Crinkle

> AI-powered Pokémon card grading for collectors and traders

---

## What is Crinkle?

Crinkle is a mobile web app that helps Pokémon card collectors estimate the grade of their cards **before** paying to submit them to professional grading services like PSA, Beckett, or CGC.

Collectors currently pay significant fees and wait weeks, sometimes months, only to receive a lower grade than expected. Crinkle eliminates that uncertainty by letting users scan a card with their phone camera and instantly receive:

- 📊 An estimated **PSA-scale grade (1–10)**
- 🔍 Detailed notes on **corners, edges, centering, and surface condition**
- 💡 Actionable insight on whether a card is worth professional grading

---

## Features

| Feature | Description |
|---|---|
|  **Card Scanner** | Scan a card with your camera for instant AI grading |
|  **Grading History** | Track all your past scans and results |
|  **Price Market** | Live card pricing with history and comparison tools |
|  **User Accounts** | Register, log in, and manage your profile |
|  **Education Hub** | Learn what professional graders look for |
|  **Guest Mode** | Try the app without creating an account |

---

## Who is it for?

- **Casual collectors** who want to understand their collection's value
- **Serious investors and traders** buying and selling cards at scale
- **Beginners** new to the hobby who need grading guidance
- **Professional graders and resellers** looking for a quick pre-screen tool

---

## Tech Stack

- **Backend:** Django 4.2
- **Frontend:** Mobile-first HTML/CSS (no native app required)
- **Database:** SQLite (development)
- **Testing:** Django TestCase + Behave BDD

---

## Team

**CS 4300/5300 — Spring 2026 — Team 4 (dev4 → cust6)**

| Name | Feature |
|---|---|
| Nazanin Siavash | Account Management |
| Jeffrey Kotz | Collection |
| Tara Prasad | Camera / Card Scan |
| Bryce Holland | Grading History |
| Joshuah Jones | Price Tracking |

---

## Getting Started
```bash
# Clone the repo
git clone https://github.com/CS4300-CS5300-SP26/dev4_cust6.git
cd dev4_cust6/crinkle

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```



---

## Running Tests
```bash
# Unit + integration tests with coverage
coverage run manage.py test accounts
coverage report

# BDD tests
python manage.py behave
```

---

*Crinkle — know your grade before you pay for it.*