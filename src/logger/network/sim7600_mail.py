"""
SIM7600E-based minimal mail sender via AT commands (fallback).

WARNING:
- Sending email via raw AT commands requires the modem to support TCP socket operations
  (AT+CIPSTART, AT+SSEND) or specific SMTP AT commands. Firmware varies.
- This implementation is a best-effort skeleton: it opens a TCP connection to SMTP server
  and streams SMTP commands. You must test on your modem firmware and adjust sequences,
  APN, and timeouts.

Environment variables:
  SIM7600_SMTP_SERVER, SIM7600_SMTP_PORT, SIM7600_USER, SIM7600_PASS
  SIM7600_APN (if needed)
"""
import logging
import time
import base64
from typing import List, Optional

logger = logging.getLogger("sim7600_mail")

try:
    import serial
except Exception:
    serial = None

SMTP_SERVER = None
SMTP_PORT = None
SIM_USER = None
SIM_PASS = None

def _init_from_env():
    global SMTP_SERVER, SMTP_PORT, SIM_USER, SIM_PASS
    import os
    SMTP_SERVER = os.environ.get("SIM7600_SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SIM7600_SMTP_PORT", "587"))
    SIM_USER = os.environ.get("SIM7600_SMTP_USER")
    SIM_PASS = os.environ.get("SIM7600_SMTP_PASS")

def _send_at(ser, cmd, wait=1.0):
    ser.write((cmd + "\r\n").encode('utf-8'))
    time.sleep(wait)
    out = b""
    while ser.in_waiting:
        out += ser.read(ser.in_waiting)
    return out.decode('utf-8', errors='ignore')

def _open_serial(port="/dev/ttyUSB2", baud=115200, timeout=1):
    if serial is None:
        raise RuntimeError("pyserial not available")
    ser = serial.Serial(port, baud, timeout=1)
    return ser

def send_email_via_sim7600(subject: str, body: str, attachments: Optional[List[str]] = None, serial_port: str = "/dev/ttyUSB2") -> bool:
    """
    Best-effort method:
    - Configure GPRS (APN) first
    - Establish TCP connection to SMTP server
    - Perform SMTP handshake and send message using raw SMTP commands
    NOTE: Many SMTP servers require TLS; implementing STARTTLS over raw TCP via AT is complex.
    This approach often fails with modern SMTP providers. Prefer SMTP via requests or GSM provider APIs.
    """
    _init_from_env()
    if serial is None:
        logger.error("pyserial not installed; cannot use SIM7600 fallback")
        return False
    try:
        ser = _open_serial(serial_port)
        logger.info("Opened serial to SIM7600 on %s", serial_port)
        # Basic modem check
        _send_at(ser, "AT", 0.2)
        _send_at(ser, "ATE0", 0.2)
        # set APN if provided (you might need to change to your provider)
        apn = __import__("os").environ.get("SIM7600_APN")
        if apn:
            _send_at(ser, f'AT+SAPBR=3,1,"Contype","GPRS"', 0.2)
            _send_at(ser, f'AT+SAPBR=3,1,"APN","{apn}"', 0.5)
            _send_at(ser, "AT+SAPBR=1,1", 2)
        # Try to open TCP connection to SMTP server
        _send_at(ser, f'AT+CIPSHUT', 0.5)
        _send_at(ser, 'AT+CIPMUX=0', 0.2)
        _send_at(ser, f'AT+CIPSTART="TCP","{SMTP_SERVER}","{SMTP_PORT}"', 5)
        # Wait and check IP status
        time.sleep(2)
        # Now, attempt simple SMTP conversation (not encrypted). For TLS STARTTLS, this won't work.
        # Many providers require TLS so this will likely fail for Gmail. Provided as fallback only.
        # Send HELO / MAIL FROM / RCPT TO / DATA etc.
        # The modem needs to support AT+SEND or AT+CIPSEND to send raw TCP data.
        _send_at(ser, "AT+CIPSEND", 0.5)
        # Build SMTP message
        to_addr = __import__("os").environ.get("KABOT_RECIPIENT", "bussenathan@icloud.com")
        from_addr = __import__("os").environ.get("KABOT_EMAIL_FROM", "kabot@example.com")
        lines = []
        lines.append(f"HELO kabot")
        lines.append(f"MAIL FROM: <{from_addr}>")
        lines.append(f"RCPT TO: <{to_addr}>")
        lines.append("DATA")
        lines.append(f"Subject: {subject}")
        lines.append(f"From: {from_addr}")
        lines.append(f"To: {to_addr}")
        lines.append("")
        lines.append(body)
        lines.append(".")
        raw = "\r\n".join(lines) + "\r\n"
        # Send raw content via CIPSEND: some modems require a size prefix. We attempt to write directly.
        ser.write(raw.encode("utf-8"))
        time.sleep(2)
        # Close connection
        _send_at(ser, "AT+CIPCLOSE", 0.5)
        _send_at(ser, "AT+CIPSHUT", 0.5)
        ser.close()
        logger.info("SIM7600 attempted to send SMTP (non TLS). Success depends on server and firmware.")
        return True
    except Exception:
        logger.exception("SIM7600 email send failed")
        return False
