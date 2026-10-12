import smtplib
from html import escape
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
    smtp_port: int = 587,
    cc_email: str = ""
) -> dict:
    """
    Sends an email with the Japanese translation as primary content
    and the original English text as reference.

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = recipient_email
        if cc_email:
            msg["Cc"] = cc_email
        msg["Subject"] = subject
        safe_japanese = escape(japanese_body).replace("\n", "<br>")
        safe_english = escape(english_body).replace("\n", "<br>")

        
        plain_body = (
            f"{japanese_body}\n"
            f"\n"
            f"{'─' * 40}\n"
            f"📝 Original (English):\n"
            f"{english_body}\n"
        )

        html_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #d63384; margin-top: 0;">🇯🇵 Japanese Translation</h3>
                <p style="font-size: 16px; line-height: 1.6;">{safe_japanese}</p>
            </div>
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px;">
                <h3 style="color: #856404; margin-top: 0;">🇬🇧 Original (English)</h3>
                <p style="font-size: 14px; line-height: 1.6; color: #666;">{safe_english}</p>
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

        recipients = [recipient_email]
        if cc_email:
            recipients.append(cc_email)

        server = None
        try:
            if smtp_port == 587:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                server.ehlo()
                if not server.has_extn("STARTTLS"):
                    raise smtplib.SMTPNotSupportedError(
                        "The SMTP server does not advertise STARTTLS on this port."
                    )
                server.starttls()
                server.ehlo()

            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        finally:
            if server is not None:
                try:
                    server.quit()
                except (smtplib.SMTPException, OSError):
                    server.close()

        return {"success": True, "message": "Email sent successfully!"}

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "Authentication failed. Check your email/App Password."}
    except smtplib.SMTPConnectError:
        return {"success": False, "message": "SMTP connection failed. Check the SMTP host/port and ensure the sender account is Gmail-compatible."}
    except (smtplib.SMTPServerDisconnected, OSError) as e:
        return {"success": False, "message": f"SMTP connection was closed: {str(e)}. For Gmail use smtp.gmail.com with port 587 (STARTTLS) or 465 (SSL)."}
    except smtplib.SMTPException as e:
        return {"success": False, "message": f"SMTP error: {str(e)}. If using Gmail, ensure 2-step verification is enabled and you are using an App Password."}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}