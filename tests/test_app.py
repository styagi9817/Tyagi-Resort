"""
Regression test suite for Tyagi Resort website.
Run with:  pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from app import app as flask_app


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["MAIL_SUPPRESS_SEND"] = True   # never send real emails in tests
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def valid_form_data():
    return {
        "name": "Rahul Tyagi",
        "email": "test@example.com",
        "phone": "9876543210",
        "event_type": "Wedding / Shaadi",
        "event_date": "2025-12-20",
        "guests": "101 – 200",
        "venue_pref": "Outdoor Lawn",
        "message": "Please arrange vegetarian menu.",
    }


# ─────────────────────────────────────────────
# TC-01  HOME PAGE
# ─────────────────────────────────────────────

class TestHomePage:
    def test_home_returns_200(self, client):
        """Home page should respond with HTTP 200."""
        res = client.get("/")
        assert res.status_code == 200

    def test_home_contains_brand_name(self, client):
        """Home page must display the resort name."""
        res = client.get("/")
        assert b"Tyagi Resort" in res.data

    def test_home_contains_catering_link(self, client):
        """Home page must link to the catering enquiry page."""
        res = client.get("/")
        assert b"catering-enquiry" in res.data or b"Catering" in res.data

    def test_home_sections_present(self, client):
        """Critical sections must be present on the home page."""
        res = client.get("/")
        html = res.data.decode()
        for section_id in ["about", "rooms", "amenities", "gallery", "contact"]:
            assert f'id="{section_id}"' in html, f"Section '{section_id}' not found"

    def test_home_nav_links(self, client):
        """Navbar navigation links should be rendered."""
        res = client.get("/")
        html = res.data.decode()
        for label in ["Rooms", "Gallery", "Contact", "Amenities"]:
            assert label in html


# ─────────────────────────────────────────────
# TC-02  CATERING ENQUIRY PAGE (GET)
# ─────────────────────────────────────────────

class TestCateringPageGet:
    def test_catering_get_returns_200(self, client):
        """GET /catering-enquiry should return HTTP 200."""
        res = client.get("/catering-enquiry")
        assert res.status_code == 200

    def test_catering_page_has_form(self, client):
        """Page must render the enquiry form."""
        res = client.get("/catering-enquiry")
        assert b"<form" in res.data

    def test_catering_required_fields_present(self, client):
        """All required form fields must be rendered."""
        res = client.get("/catering-enquiry")
        html = res.data.decode()
        for field in ["name", "email", "phone", "event_type", "event_date", "guests"]:
            assert f'name="{field}"' in html, f"Field '{field}' missing from form"

    def test_catering_submit_button_present(self, client):
        """A submit button must exist on the form."""
        res = client.get("/catering-enquiry")
        assert b'type="submit"' in res.data

    def test_catering_privacy_note_present(self, client):
        """Privacy / email note referencing resort email should appear."""
        res = client.get("/catering-enquiry")
        assert b"styagi9817@gmail.com" in res.data


# ─────────────────────────────────────────────
# TC-03  CATERING FORM – VALID SUBMISSION
# ─────────────────────────────────────────────

class TestCateringFormValidSubmission:
    @patch("app.mail")
    def test_valid_submission_redirects_to_thankyou(self, mock_mail, client, valid_form_data):
        """Valid form POST should redirect to the thank-you page."""
        mock_mail.send = MagicMock()
        res = client.post("/catering-enquiry", data=valid_form_data, follow_redirects=False)
        assert res.status_code == 302
        assert "/thank-you" in res.headers["Location"]

    @patch("app.mail")
    def test_valid_submission_sends_two_emails(self, mock_mail, client, valid_form_data):
        """Two emails should be sent: one to resort, one to enquirer."""
        mock_mail.send = MagicMock()
        client.post("/catering-enquiry", data=valid_form_data, follow_redirects=True)
        assert mock_mail.send.call_count == 2

    @patch("app.mail")
    def test_email_to_resort_address(self, mock_mail, client, valid_form_data):
        """First email must target the resort address."""
        captured = []
        mock_mail.send = lambda msg: captured.append(msg)
        client.post("/catering-enquiry", data=valid_form_data, follow_redirects=True)
        resort_emails = [m for m in captured if "styagi9817@gmail.com" in m.recipients]
        assert len(resort_emails) >= 1

    @patch("app.mail")
    def test_confirmation_email_to_enquirer(self, mock_mail, client, valid_form_data):
        """Confirmation email must target the form's email address."""
        captured = []
        mock_mail.send = lambda msg: captured.append(msg)
        client.post("/catering-enquiry", data=valid_form_data, follow_redirects=True)
        enquirer_emails = [m for m in captured if valid_form_data["email"] in m.recipients]
        assert len(enquirer_emails) >= 1

    @patch("app.mail")
    def test_resort_email_body_contains_event_details(self, mock_mail, client, valid_form_data):
        """Resort notification email body must include key event details."""
        captured = []
        mock_mail.send = lambda msg: captured.append(msg)
        client.post("/catering-enquiry", data=valid_form_data, follow_redirects=True)
        resort_msg = [m for m in captured if "styagi9817@gmail.com" in m.recipients][0]
        assert valid_form_data["name"] in resort_msg.body
        assert valid_form_data["event_type"] in resort_msg.body
        assert valid_form_data["guests"] in resort_msg.body


# ─────────────────────────────────────────────
# TC-04  CATERING FORM – INVALID SUBMISSIONS
# ─────────────────────────────────────────────

class TestCateringFormValidation:
    def test_missing_name_shows_error(self, client, valid_form_data):
        """Omitting 'name' should re-render the form with an error."""
        data = {**valid_form_data, "name": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert res.status_code == 200
        assert b"Name is required" in res.data

    def test_missing_email_shows_error(self, client, valid_form_data):
        """Omitting 'email' should re-render the form with an error."""
        data = {**valid_form_data, "email": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"valid email" in res.data

    def test_invalid_email_format_shows_error(self, client, valid_form_data):
        """Supplying an invalid email should trigger a validation error."""
        data = {**valid_form_data, "email": "not-an-email"}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"valid email" in res.data

    def test_missing_phone_shows_error(self, client, valid_form_data):
        data = {**valid_form_data, "phone": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"Phone" in res.data

    def test_missing_event_type_shows_error(self, client, valid_form_data):
        data = {**valid_form_data, "event_type": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"Event type" in res.data

    def test_missing_event_date_shows_error(self, client, valid_form_data):
        data = {**valid_form_data, "event_date": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"Event date" in res.data

    def test_missing_guests_shows_error(self, client, valid_form_data):
        data = {**valid_form_data, "guests": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert b"guests" in res.data.lower()

    def test_completely_empty_form_shows_multiple_errors(self, client):
        """Submitting a blank form should return multiple error messages."""
        res = client.post("/catering-enquiry", data={}, follow_redirects=True)
        assert res.status_code == 200
        html = res.data.decode()
        assert html.count("alert") >= 3

    def test_invalid_submission_preserves_valid_fields(self, client, valid_form_data):
        """Valid field values should be preserved on re-render."""
        data = {**valid_form_data, "name": ""}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        assert valid_form_data["phone"].encode() in res.data


# ─────────────────────────────────────────────
# TC-05  MAIL FAILURE GRACEFUL HANDLING
# ─────────────────────────────────────────────

class TestMailFailureHandling:
    @patch("app.mail")
    def test_mail_failure_redirects_to_thankyou_with_warning(self, mock_mail, client, valid_form_data):
        """If mail sending raises an exception, user is still redirected to thank-you."""
        mock_mail.send = MagicMock(side_effect=Exception("SMTP error"))
        res = client.post("/catering-enquiry", data=valid_form_data, follow_redirects=True)
        assert res.status_code == 200
        assert b"Thank You" in res.data or b"thank" in res.data.lower()


# ─────────────────────────────────────────────
# TC-06  THANK-YOU PAGE
# ─────────────────────────────────────────────

class TestThankYouPage:
    def test_thankyou_get_returns_200(self, client):
        res = client.get("/thank-you")
        assert res.status_code == 200

    def test_thankyou_contains_confirmation_text(self, client):
        res = client.get("/thank-you")
        assert b"Thank You" in res.data

    def test_thankyou_has_home_link(self, client):
        res = client.get("/thank-you")
        assert b"Home" in res.data or b"/" in res.data

    def test_thankyou_has_new_enquiry_link(self, client):
        res = client.get("/thank-you")
        assert b"catering-enquiry" in res.data or b"Enquiry" in res.data


# ─────────────────────────────────────────────
# TC-07  HEALTH CHECK ENDPOINT
# ─────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_returns_json_ok(self, client):
        res = client.get("/health")
        data = res.get_json()
        assert data is not None
        assert data.get("status") == "ok"


# ─────────────────────────────────────────────
# TC-08  404 HANDLING
# ─────────────────────────────────────────────

class TestNotFound:
    def test_unknown_route_returns_404(self, client):
        res = client.get("/this-page-does-not-exist")
        assert res.status_code == 404


# ─────────────────────────────────────────────
# TC-09  SECURITY HEADERS / XSS CHECK
# ─────────────────────────────────────────────

class TestSecurityBasics:
    def test_no_script_injection_in_form_echo(self, client, valid_form_data):
        """XSS payload in name should be escaped, not executed."""
        data = {**valid_form_data, "name": "<script>alert(1)</script>", "email": "bad-email"}
        res = client.post("/catering-enquiry", data=data, follow_redirects=True)
        html = res.data.decode()
        assert "<script>alert(1)</script>" not in html
        # Jinja2 auto-escapes so the angle brackets should be HTML-encoded
        assert "&lt;script&gt;" in html or "script" not in html.lower()

    def test_method_not_allowed_on_home(self, client):
        """POST to the home route should return 405."""
        res = client.post("/")
        assert res.status_code == 405
