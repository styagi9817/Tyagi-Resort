import os
import requests as http_requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tyagi-resort-secret-2024")

RESORT_EMAIL   = "styagi9817@gmail.com"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
MAIL_ENABLED   = bool(RESEND_API_KEY)

# Startup diagnostic – visible in Render logs
print(f"[MAIL] MAIL_ENABLED={MAIL_ENABLED}  method=Resend-HTTPS  api_key_len={len(RESEND_API_KEY)}", flush=True)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send email via Resend HTTPS API — no SMTP ports needed."""
    if not MAIL_ENABLED:
        print("[MAIL] Skipped – RESEND_API_KEY not set", flush=True)
        return False
    try:
        resp = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from":    "Tyagi Resort <onboarding@resend.dev>",
                "to":      [to],
                "subject": subject,
                "text":    body,
            },
            timeout=15,
        )
        if resp.status_code in (200, 201):
            print(f"[MAIL] Sent OK → {to}", flush=True)
            return True
        print(f"[MAIL] Resend error {resp.status_code}: {resp.text}", flush=True)
        return False
    except Exception as exc:
        print(f"[MAIL] Exception: {exc}", flush=True)
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/catering-enquiry", methods=["GET", "POST"])
def catering_enquiry():
    if request.method == "POST":
        name       = request.form.get("name", "").strip()
        email      = request.form.get("email", "").strip()
        phone      = request.form.get("phone", "").strip()
        event_type = request.form.get("event_type", "").strip()
        event_date = request.form.get("event_date", "").strip()
        guests     = request.form.get("guests", "").strip()
        message    = request.form.get("message", "").strip()

        # Validation
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not event_type:
            errors.append("Event type is required.")
        if not event_date:
            errors.append("Event date is required.")
        if not guests:
            errors.append("Number of guests is required.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("catering.html", form_data=request.form)

        # Notify resort
        send_email(
            to=RESORT_EMAIL,
            subject=f"New Booking Enquiry – {event_type} | {name}",
            body=f"""New Booking Enquiry Received
==============================
Name         : {name}
Email        : {email}
Phone        : {phone}
Event Type   : {event_type}
Event Date   : {event_date}
No. of Guests: {guests}

Message:
{message}
""",
        )

        # Confirm to enquirer
        send_email(
            to=email,
            subject="Thank you for your enquiry – Tyagi Resort",
            body=f"""Dear {name},

Thank you for reaching out to Tyagi Resort! We have received your booking enquiry
for a {event_type} on {event_date} for {guests} guests.

Our team will get in touch with you shortly at {phone} or {email}.

Warm regards,
Tyagi Resort Team
styagi9817@gmail.com
""",
        )

        flash("Your enquiry has been submitted successfully! We will contact you soon.", "success")
        return redirect(url_for("thank_you"))

    return render_template("catering.html", form_data={})


@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html")


@app.route("/test-email")
def test_email():
    """Diagnostic route – visit to verify Resend API is working."""
    if not MAIL_ENABLED:
        return jsonify(status="MAIL_DISABLED", reason="RESEND_API_KEY env var not set on Render"), 503
    ok = send_email(
        to=RESORT_EMAIL,
        subject="Tyagi Resort – Email Test",
        body="This is a test email confirming Resend API is working correctly.",
    )
    if ok:
        return jsonify(status="OK", message=f"Test email sent to {RESORT_EMAIL}"), 200
    return jsonify(status="ERROR", detail="Check Render logs for details"), 500


@app.route("/health")
def health():
    return jsonify(status="ok", mail_enabled=MAIL_ENABLED), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
