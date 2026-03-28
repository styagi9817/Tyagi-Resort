# Tyagi Resort Website

An attractive, fully functional luxury resort website built with **Python / Flask**, featuring:

- Beautiful multi-section landing page (Hero, About, Rooms, Amenities, Gallery, Testimonials, Contact)
- Catering Enquiry form with email notifications (Gmail SMTP via Flask-Mail)
- Client-side + server-side form validation
- Gallery with a lightbox viewer
- Animated counters, smooth scroll, AOS animations
- Full regression test suite (34 tests, 100% pass rate)
- Ready for **Heroku** deployment

---

## Project Structure

```
Tyagi_Resort_website/
├── app.py                  # Flask application
├── Procfile                # Heroku process file
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version for Heroku
├── .env.example            # Template for environment variables
├── .gitignore
├── templates/
│   ├── base.html           # Shared layout (navbar, footer)
│   ├── index.html          # Home page
│   ├── catering.html       # Catering enquiry form page
│   └── thankyou.html       # Confirmation page
├── static/
│   ├── css/style.css       # Custom styles
│   └── js/main.js          # Interactivity (AOS, counters, lightbox)
└── tests/
    └── test_app.py         # 34 regression tests
```

---

## Local Development

### 1. Clone & set up environment

```bash
cd Tyagi_Resort_website
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in:
#   SECRET_KEY      – any long random string
#   MAIL_USERNAME   – styagi9817@gmail.com
#   MAIL_PASSWORD   – Gmail App Password (see note below)
```

> **Gmail App Password**: Go to [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords)  
> Create an app password for "Mail" and paste it as `MAIL_PASSWORD`.

### 3. Run locally

```bash
python app.py
```
Open http://localhost:5000

---

## Running Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

Expected: **34 passed** in ~2s

---

## Deploy to Heroku

### Prerequisites
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed and logged in
- Git installed

### Steps

```bash
# 1. Initialise git repo
git init
git add .
git commit -m "Initial commit – Tyagi Resort website"

# 2. Create Heroku app
heroku create tyagi-resort        # or any available name

# 3. Set environment variables on Heroku
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set MAIL_USERNAME="styagi9817@gmail.com"
heroku config:set MAIL_PASSWORD="your-gmail-app-password"

# 4. Deploy
git push heroku main              # or: git push heroku master

# 5. Open the live site
heroku open
```

### Verify deployment
```bash
heroku logs --tail         # stream live logs
curl https://<your-app>.herokuapp.com/health   # should return {"status":"ok"}
```

---

## Email Configuration Notes

| Setting | Value |
|---------|-------|
| SMTP Server | smtp.gmail.com |
| Port | 587 (TLS) |
| Sender / Resort Email | styagi9817@gmail.com |
| Auth | Gmail App Password |

When a visitor submits the catering form:
1. A **notification email** is sent to `styagi9817@gmail.com` with full event details.
2. A **confirmation email** is sent back to the visitor.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3 |
| Email | Flask-Mail + Gmail SMTP |
| Frontend | Bootstrap 5, Animate On Scroll (AOS) |
| Fonts | Google Fonts – Playfair Display, Lato |
| Icons | Font Awesome 6 |
| Testing | pytest |
| Hosting | Heroku (Gunicorn WSGI) |
