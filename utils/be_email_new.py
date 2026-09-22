import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import re
import random
from pathlib import Path
from datetime import datetime
import json


import logging
logger = logging.getLogger(__name__)

# This may need to be changed if it changes.
# smtp_server = '172.17.33.25'
smtp_server = 'itapps02.blueeaglecu.org'
smtp_port = 25
sender_email = 'Seecil <seecil@blueeaglecreditunion.com>'

email_dir = Path("C:/Scripts/Utilities/be_email")

def process_email(email_json):
    
    with open(email_json, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    all_recipients = data["receivers"] + data["bcc"]
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(data["receivers"])
    msg["Subject"] = data["subject"]
    msg.attach(MIMEText(data["body"], "plain"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.send_message(msg, to_addrs=all_recipients)
            print(f'Email sent successfully to: {msg["To"]}')
            return True
    except Exception as e:
        print(f'Failed to send email: {e}')
        return False

def send(rec=None, subject=None, body=None):
    
    rec = rec or 'tyler.giles@blueeaglecreditunion.com'
    subject = subject or f'New Test Email via {smtp_server}:{smtp_port}'
    body = body or f'Hello, this is a test email sent via SMTP server: {smtp_server}:{smtp_port}'
    
    if isinstance(rec, str):
        receivers = re.split(r'[ ,]+', rec)
    elif isinstance(rec, list):
        receivers = rec
    else:
        logger.error("Receiver emails neither a list nor a string. Cannot send email...")
        return
    
    receiver_final = []
    bcc_list = []
        
    for addr in receivers:
        
        if "@" in addr: sel_addr = addr.strip()
        else: sel_addr = f"{addr}@blueeaglecreditunion.com".strip()
        
        match = re.match(r"^bcc-(.*)", sel_addr, re.IGNORECASE)
        if match: bcc_list.append(match.group(1))
        else: receiver_final.append(sel_addr)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    data = {
        "timestamp": timestamp,
        "receivers": receiver_final,
        "bcc": bcc_list,
        "subject": subject,
        "body": body
    }
    
    email_json = email_dir / f"{timestamp}.json"
    email_json.parent.mkdir(parents=True, exist_ok=True)
    
    with open(email_json, "w", encoding="utf8") as file:
        json.dump(data, file, indent=4)
    
    process_email(email_json)
        
        
def seecil_closes():
    
    closings = [
        # Christmas Season Ones
        #"🎅 Swooping down the chimney",
        #"🎄 Talon the halls",
        #"❄️ Talon-tidings",
        #"☃️ Festive and feathered",
        #"🎄 Wings up, ornaments out",
        #"🎄 Nesting by the tree"
        "Counting feathers and funds",
        "Feathered and focused",
        "Swooping out",
        "Stay talon-ted",
        "Soaring off for now",
        "Soaring expectations",
        "Flapping and funding",
        "Landing shortly",
        "Feathers up",
        "🦅 From the highest branch",
        "Nesting and investing",
        "Funding on the fly",
        "No talon what's next",
        "Wings up, rates down",
        "Taking it to the nest level",
        "Eagle eye on the prize",
        "Ready for takeoff",
        "Securing nest eggs",
        "Soaring on schedule",
        "Blue skies ahead"
    ]
    
    
    return random.choice(closings)