import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings


def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> bool:
    """Send an email using SMTP."""
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email

        # Add text part
        text_part = MIMEText(body_text, "plain")
        msg.attach(text_part)

        # Add HTML part if provided
        if body_html:
            html_part = MIMEText(body_html, "html")
            msg.attach(html_part)

        # Create SMTP connection
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            # Send email
            server.send_message(msg)

        return True
    except Exception:
        return False


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send password reset email."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    subject = "Password Reset Request"

    text_body = f"""
    Hello,

    You have requested to reset your password. Please click the link below to reset it:

    {reset_url}

    If you did not request this reset, please ignore this email.

    This link will expire in 24 hours.

    Best regards,
    Your Journal App Team
    """

    html_body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You have requested to reset your password. Please click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>If you did not request this reset, please ignore this email.</p>
            <p>This link will expire in 24 hours.</p>
            <p>Best regards,<br>Your Journal App Team</p>
        </body>
    </html>
    """

    return send_email(to_email, subject, text_body, html_body)
