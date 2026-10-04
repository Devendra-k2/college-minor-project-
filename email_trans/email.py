# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    japanese_body: str,
    english_body: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> dict:
    """
    Sends an email with the Japanese translation as primary content
    and the original English text as reference.

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    try:
        # --- Build the email ---
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Plain text version
        plain_body = (
            f"{japanese_body}\n"
            f"\n"
            f"{'─' * 40}\n"
            f"📝 Original (English):\n"
            f"{english_body}\n"
        )

        # HTML version (looks nicer in email clients)
        html_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #d63384; margin-top: 0;">🇯🇵 Japanese Translation</h3>
                <p style="font-size: 16px; line-height: 1.6;">{japanese_body}</p>
            </div>
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px;">
                <h3 style="color: #856404; margin-top: 0;">🇬🇧 Original (English)</h3>
                <p style="font-size: 14px; line-height: 1.6; color: #666;">{english_body}</p>
            </div>
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 11px; color: #999; text-align: center;">
                Translated using English-to-Japanese Email Translator
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # --- Send the email ---
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()                           # Secure the connection
            server.login(sender_email, sender_password) # Login
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return {"success": True, "message": "Email sent successfully!"}

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "Authentication failed. Check your email/App Password."}
    except smtplib.SMTPException as e:
        return {"success": False, "message": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}