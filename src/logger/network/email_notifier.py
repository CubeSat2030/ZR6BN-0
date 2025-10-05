"""
Email notifier with two backends:
- SMTP via Gmail (recommended) using TLS (smtp.gmail.com:587).
  Use environment variables:
    EMAIL_FROM       (e.g. your Gmail address)
    EMAIL_TO         (comma separated, by default uses bussenathan@icloud.com)
    EMAIL_USERNAME   (your Gmail address or service account)
    EMAIL_PASSWORD   (app password — recommended for Gmail)
- SIM7600E AT-based fallback using sim7600_mail.py (serial AT approach).
"""

import os
import logging
import smtplib
import mimetypes
from email.message import EmailMessage
from typing import List, Optional

logger = logging.getLogger("email_notifier")

# default recipient (user supplied)
DEFAULT_TO = os.environ.get("KABOT_RECIPIENT", "bussenathan@icloud.com")

# environment variables to configure
SMTP_SERVER = os.environ.get("KABOT_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("KABOT_SMTP_PORT", "587"))
EMAIL_FROM = os.environ.get("KABOT_EMAIL_FROM")
EMAIL_TO = os.environ.get("KABOT_EMAIL_TO", DEFAULT_TO)
EMAIL_USERNAME = os.environ.get("KABOT_EMAIL_USER", EMAIL_FROM)
EMAIL_PASSWORD = os.environ.get("KABOT_EMAIL_PASS")  # app password recommended

# SIM7600 fallback
USE_SIM_FALLBACK = os.environ.get("KABOT_USE_SIM_FALLBACK", "1") == "1"
SIM7600_SERIAL_PORT = os.environ.get("KABOT_SIM_PORT", "/dev/ttyUSB2")

def _attach_file(msg: EmailMessage, path: str):
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    with open(path, "rb") as fh:
        data = fh.read()
    msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))

def send_email_smtp(subject: str, body: str, attachments: Optional[List[str]] = None, to_addrs: Optional[List[str]] = None) -> bool:
    """
    Send email via SMTP (Gmail or other).
    Returns True on success.
    """
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        logger.warning("SMTP credentials not configured; cannot send via SMTP")
        return False
    to_addrs = to_addrs or [EMAIL_TO]
    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)
    attachments = attachments or []
    for p in attachments:
        try:
            _attach_file(msg, p)
        except Exception:
            logger.exception("Failed to attach %s", p)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info("SMTP email sent to %s", to_addrs)
        return True
    except Exception:
        logger.exception("SMTP send failed")
        return False

def send_email(subject: str, body: str, attachments: Optional[List[str]] = None, to_addrs: Optional[List[str]] = None) -> bool:
    """
    Try SMTP first; if it fails and SIM fallback is enabled, attempt to use SIM7600 AT sender.
    """
    success = send_email_smtp(subject, body, attachments, to_addrs)
    if success:
        return True
    if USE_SIM_FALLBACK:
        try:
            from .sim7600_mail import send_email_via_sim7600
            logger.info("Attempting SIM7600 email fallback")
            return send_email_via_sim7600(subject, body, attachments, SIM7600_SERIAL_PORT)
        except Exception:
            logger.exception("SIM7600 fallback failed or not implemented")
    return False
