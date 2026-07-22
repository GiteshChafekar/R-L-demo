import random
from flask_mail import Message
from extensions import mail


def generate_otp():
    """Generate a random 6-digit OTP code."""
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(recipient_email, full_name, otp_code, expiry_minutes):
    subject = "Your Verification Code - SecureBank"
    body = f"""Hi {full_name},

Your One-Time Password (OTP) for SecureBank registration is:

    {otp_code}

This code will expire in {expiry_minutes} minutes. If you did not request this, please ignore this email.

- SecureBank Team
"""
    msg = Message(subject=subject, recipients=[recipient_email], body=body)
    mail.send(msg)
