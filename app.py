import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tyagi-resort-secret-2024")

# Flask-Mail configuration — port 465 (SSL) works on Render free tier
# Strip spaces from App Password — Google shows it as "xxxx xxxx xxxx xxxx"
_mail_password = os.environ.get("MAIL_PASSWORD", "").replace(" ", "").strip()
_mail_user    = os.environ.get("MAIL_USERNAME", "styagi9817@gmail.com").strip()

app.config["MAIL_SERVER"]         = "smtp.gmail.com"
app.config["MAIL_PORT"]           = 465
app.config["MAIL_USE_SSL"]        = True
app.config["MAIL_USE_TLS"]        = False
app.config["MAIL_USERNAME"]       = _mail_user
app.config["MAIL_PASSWORD"]       = _mail_password
app.config["MAIL_DEFAULT_SENDER"] = _mail_user
app.config["MAIL_TIMEOUT"]        = 15

mail = Mail(app)

RESORT_EMAIL  = "styagi9817@gmail.com"
MAIL_ENABLED  = bool(_mail_password)

# Startup diagnostic – visible in Render logs
print(f"[MAIL] MAIL_ENABLED={MAIL_ENABLED}  port=465/SSL  username={_mail_user}  password_len={len(_mail_password)}", flush=True)


def send_async_email(app_ctx, msg):
    """Send email in a non-daemon background thread."""
    with app_ctx:
        try:
            mail.send(msg)
            print(f"[MAIL] Sent OK → {msg.recipients}", flush=True)
        except Exception as exc:
            print(f"[MAIL] ERROR sending to {msg.recipients}: {exc}", flush=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/catering-enquiry", methods=["GET", "POST"])
def catering_enquiry():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        event_type = request.form.get("event_type", "").strip()
        event_date = request.form.get("event_date", "").strip()
        guests = request.form.get("guests", "").strip()
        message = request.form.get("message", "").strip()

        # Basic validation
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
            return render_template(
                "catering.html",
                form_data=request.form,
            )

        # Send emails in background threads (non-blocking) so the worker never hangs
        if MAIL_ENABLED:
            resort_msg = Message(
                subject=f"New Booking Enquiry – {event_type} | {name}",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[RESORT_EMAIL],
            )
            resort_msg.body = f"""
New Booking Enquiry Received
==============================
Name         : {name}
Email        : {email}
Phone        : {phone}
Event Type   : {event_type}
Event Date   : {event_date}
No. of Guests: {guests}

Message:
{message}
"""
            threading.Thread(
                target=send_async_email,
                args=(app.app_context(), resort_msg),
                daemon=False,   # non-daemon: thread completes before process can exit
            ).start()

            confirm_msg = Message(
                subject="Thank you for your enquiry – Tyagi Resort",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email],
            )
            confirm_msg.body = f"""
Dear {name},

Thank you for reaching out to Tyagi Resort! We have received your booking enquiry
for a {event_type} on {event_date} for {guests} guests.

Our team will get in touch with you shortly at {phone} or {email}.

Warm regards,
Tyagi Resort Team
styagi9817@gmail.com
"""
            threading.Thread(
                target=send_async_email,
                args=(app.app_context(), confirm_msg),
                daemon=False,   # non-daemon: thread completes before process can exit
            ).start()
        else:
            print(f"[MAIL] SKIPPED – MAIL_ENABLED is False. Check MAIL_PASSWORD env var on Render.", flush=True)

        flash(
            "Your enquiry has been submitted successfully! We will contact you soon.",
            "success",
        )
        return redirect(url_for("thank_you"))

    return render_template("catering.html", form_data={})


@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html")


@app.route("/test-email")
def test_email():
    """Diagnostic route – visit this URL to verify email config is working."""
    if not MAIL_ENABLED:
        return jsonify(status="MAIL_DISABLED", reason="MAIL_PASSWORD env var is not set or empty"), 503
    try:
        msg = Message(
            subject="Tyagi Resort – Email Test",
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[RESORT_EMAIL],
        )
        msg.body = "This is a test email from Tyagi Resort to confirm SMTP is working correctly."
        mail.send(msg)
        print(f"[MAIL] /test-email OK → {RESORT_EMAIL}", flush=True)
        return jsonify(status="OK", message=f"Test email sent to {RESORT_EMAIL}"), 200
    except BaseException as exc:
        err = str(exc)
        print(f"[MAIL] /test-email ERROR: {err}", flush=True)
        return jsonify(status="ERROR", detail=err), 500


@app.route("/health")
def health():
    """Health-check endpoint."""
    return {"status": "ok", "mail_enabled": MAIL_ENABLED}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
