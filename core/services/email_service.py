import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))

    def send_email(self, to_email, subject, content):
        email = Mail(
            from_email="gustavobdsdev@gmail.com",
            to_emails=to_email,
            subject=subject,
            html_content=content,
        )
        try:
            response = self.sg.send(email)
            print(f"Status Code: {response.status_code}")
            print(f"Body: {response.body}")
            print(f"Headers: {response.headers}")
        except Exception as e:
            print(f"Error: {e}")
