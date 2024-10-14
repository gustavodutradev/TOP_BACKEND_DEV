import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))

    def send_email(self, to_email, subject, content, is_html=False):
        email = Mail(
            from_email="gustavobdsdev@gmail.com",
            to_emails=to_email,
            subject=subject,
            html_content=content if is_html else None,
        )

        if not is_html:
            email.text = content

        try:
            self.sg.send(email)
        except Exception as e:
            print(f"Error: {str(e)}")
            if hasattr(e, "body"):
                print(f"Body: {e.body}")
