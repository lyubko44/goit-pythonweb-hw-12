import smtplib
from email.mime.text import MIMEText


def send_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "your_email@example.com"
    msg["To"] = to

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.sendmail("your_email@example.com", to, msg.as_string())
