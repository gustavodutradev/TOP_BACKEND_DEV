import os
import logging
from typing import Union, List
from dataclasses import dataclass
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, EmailContent

@dataclass
class EmailConfig:
    """Configuration for email sending"""
    from_email: str = "compliance@topinvgroup.com"
    api_key_env_var: str = "SENDGRID_API_KEY"

class EmailServiceException(Exception):
    """Custom exception for email service errors"""
    pass

class EmailService:
    """Service for sending emails using SendGrid"""
    
    def __init__(self, config: EmailConfig = None):
        """
        Initialize EmailService with configuration
        
        Args:
            config: EmailConfig object with service configuration
        
        Raises:
            EmailServiceException: If SendGrid API key is not found
        """
        self.config = config or EmailConfig()
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get(self.config.api_key_env_var)
        
        if not self.api_key:
            raise EmailServiceException(f"SendGrid API key not found in environment variable: {self.config.api_key_env_var}")
            
        self.sg = SendGridAPIClient(self.api_key)

    def _parse_email_addresses(self, emails: Union[str, List[str]]) -> List[str]:
        """
        Parse email addresses from string or list format
        
        Args:
            emails: String of comma-separated emails or list of email addresses
            
        Returns:
            List of email addresses
        """
        if isinstance(emails, str):
            return [email.strip() for email in emails.split(",") if email.strip()]
        return [email.strip() for email in emails if email.strip()]

    def _create_email_content(self, content: str, is_html: bool) -> EmailContent:
        """
        Create appropriate email content based on type
        
        Args:
            content: Email content
            is_html: Whether the content is HTML
            
        Returns:
            EmailContent object
        """
        content_type = 'text/html' if is_html else 'text/plain'
        return Content(content_type, content)

    def send_email(
        self, 
        to_emails: Union[str, List[str]], 
        subject: str, 
        content: str, 
        is_html: bool = False
    ) -> bool:
        """
        Send email using SendGrid
        
        Args:
            to_emails: Recipient email address(es)
            subject: Email subject
            content: Email content
            is_html: Whether the content is HTML
            
        Returns:
            bool: True if email was sent successfully, False otherwise
            
        Raises:
            EmailServiceException: If there's an error sending the email
        """
        try:
            parsed_emails = self._parse_email_addresses(to_emails)
            
            if not parsed_emails:
                raise EmailServiceException("No valid email addresses provided")

            email_content = self._create_email_content(content, is_html)
            
            message = Mail(
                from_email=Email(self.config.from_email),
                to_emails=[To(email) for email in parsed_emails],
                subject=subject,
                content=email_content
            )

            response = self.sg.send(message)
            
            if response.status_code not in range(200, 300):
                raise EmailServiceException(f"Failed to send email. Status code: {response.status_code}")

            self.logger.info(f"Email sent successfully to {', '.join(parsed_emails)}")
            return True

        except Exception as e:
            error_message = f"Failed to send email: {str(e)}"
            if hasattr(e, "body"):
                error_message += f" Response body: {e.body}"
                
            self.logger.error(error_message)
            raise EmailServiceException(error_message) from e