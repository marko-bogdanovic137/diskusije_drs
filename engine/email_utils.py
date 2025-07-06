import smtplib
import os
from email.message import EmailMessage

def send_email(to_email, subject, body):
    print("⬅️ Pozvana send_email()")  # dodato

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(os.getenv('EMAIL_HOST'), int(os.getenv('EMAIL_PORT'))) as smtp:
            smtp.starttls()
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            smtp.send_message(msg)
        print("Email poslat")
        return True
    except Exception as e:
        print(f"Greška pri slanju emaila: {e}")
        return False

