import logging
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "")
    tone = data.get("tone", "Formal Keigo")
    if not isinstance(topic, str) or not topic.strip():
        return jsonify({"error": "Enter a topic to generate an email."}), 400
    if tone not in {"Formal Keigo", "Business", "Casual"}:
        return jsonify({"error": "Choose a supported email tone."}), 400

    try:
        from write_email import generate_email

        return jsonify({"email": generate_email(topic, tone)})
    except Exception:
        logging.exception("Email generation failed")
        return jsonify({"error": "Generation failed. Check the server log and API configuration."}), 500


@app.post("/api/translate")
def translate_email():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Enter an email to translate."}), 400

    try:
        from translate import translate

        return jsonify({"translation": translate(email)})
    except Exception:
        logging.exception("Email translation failed")
        return jsonify({"error": "Translation failed. Check the local translation model."}), 500


@app.post("/api/send")
def send():
    load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient", "")
    cc = data.get("cc", "")
    subject = data.get("subject", "")
    english = data.get("english", "")
    japanese = data.get("japanese", "")
    if not all(isinstance(value, str) for value in (recipient, cc, subject, english, japanese)):
        return jsonify({"error": "Email fields must be text."}), 400
    if not recipient.strip() or not subject.strip() or not english.strip() or not japanese.strip():
        return jsonify({"error": "Add a recipient, subject, English draft, and Japanese translation before sending."}), 400

    sender_email = os.getenv("SENDER_EMAIL") or os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("SENDER_PASSWORD") or os.getenv("EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        return jsonify({"error": "Sending is not configured. Set SENDER_EMAIL and SENDER_PASSWORD in email_trans/.env."}), 503

    try:
        from email_sender import send_email

        result = send_email(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient.strip(),
            subject=subject.strip(),
            japanese_body=japanese.strip(),
            english_body=english.strip(),
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            cc_email=cc.strip(),
        )
        status_code = 200 if result["success"] else 502
        return jsonify(result), status_code
    except Exception:
        logging.exception("Email send failed")
        return jsonify({"success": False, "message": "Email could not be sent. Check the SMTP configuration."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)