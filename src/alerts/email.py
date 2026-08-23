"""Email alerting utilities.

This module shows how to send email alerts using SMTP. Credentials should be provided via environment variables.
"""

import os
import smtplib
from email.message import EmailMessage


def send_email(subject: str, body: str, to: str = None):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_addr = os.getenv('ALERT_FROM')
    to_addr = to or os.getenv('ALERT_TO')

    if not (smtp_host and smtp_user and smtp_password and from_addr and to_addr):
        raise EnvironmentError("SMTP configuration is incomplete — set environment variables")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(smtp_user, smtp_password)
        s.send_message(msg)
