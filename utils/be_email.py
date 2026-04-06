import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import re

import logging
logger = logging.getLogger(__name__)

# This may need to be changed if it changes.
smtp_server = '172.17.33.25'

def send(rec=None, subject=None, body=None):
    
    rec = rec or 'tyler.giles@blueeaglecreditunion.com'
    subject = subject or f'Test Email via {smtp_server}:25'
    body = body or f'Hello, this is a test email sent via SMTP server: {smtp_server}:25'
    
    if isinstance(rec, str):
        receivers = re.split(r'[ ,]+', rec)
    elif isinstance(rec, list):
        receivers = rec
    else:
        logger.error("Receiver emails neither a list nor a string. Cannot send email...")
        return

    receiver_final = [
        addr if "@" in addr else f"{addr}@blueeaglecreditunion.com"
        for addr in receivers if addr.strip()
    ]
        
    receiver_string = ", ".join(receiver_final)
    
    smtp_port = 25
    sender_email = 'Seecil <seecil@blueeaglecreditunion.com>'
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_string
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.send_message(msg)
            return f'Email sent successfully to: {receiver_string}'
    except Exception as e:
        return f'Failed to send email: {e}'