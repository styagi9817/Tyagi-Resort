import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tyagi-resort-secret-2024")

# Flask-Mail configuration (uses Gmail SMTP)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "styagi9817@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "styagi9817@gmail.com")

mail = Mail(app)

RESORT_EMAIL = "styagi9817@gmail.com"


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

        # Send email notification to resort
        try:
            resort_msg = Message(
                subject=f"New Catering Enquiry – {event_type} | {name}",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[RESORT_EMAIL],
            )
            resort_msg.body = f"""
New Catering Enquiry Received
==============================
Name        : {name}
Email       : {email}
Phone       : {phone}
Event Type  : {event_type}
Event Date  : {event_date}
No. of Guests: {guests}

Message:
{message}
"""
            mail.send(resort_msg)

            # Send confirmation to enquirer
            confirm_msg = Message(
                subject="Thank you for your enquiry – Tyagi Resort",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email],
            )
            confirm_msg.body = f"""
Dear {name},

Thank you for reaching out to Tyagi Resort! We have received your catering enquiry
for a {event_type} on {event_date} for {guests} guests.

Our catering team will get in touch with you shortly at {phone} or {email}.

Warm regards,
Tyagi Resort Team
styagi9817@gmail.com
"""
            mail.send(confirm_msg)

            flash(
                "Your enquiry has been submitted successfully! We will contact you soon.",
                "success",
            )
            return redirect(url_for("thank_you"))

        except Exception as exc:
            app.logger.error("Mail send failed: %s", exc)
            flash(
                "Your enquiry was received but we could not send a confirmation email right now. "
                "We will still get back to you!",
                "warning",
            )
            return redirect(url_for("thank_you"))

    return render_template("catering.html", form_data={})


@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html")


@app.route("/health")
def health():
    """Health-check endpoint used by Heroku and tests."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
