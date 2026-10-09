import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email_with_attachment(pdf_path):

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    msg = EmailMessage()
    msg["Subject"] = "AI Analytics Report"
    msg["From"] = sender
    msg["To"] = receiver

    msg.set_content(
        "Attached is the latest AI Analytics PDF report."
    )

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="pdf",
        filename=os.path.basename(pdf_path)
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    return "Email Sent Successfully"