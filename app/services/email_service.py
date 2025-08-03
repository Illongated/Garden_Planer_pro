from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME
)

fm = FastMail(conf)

async def send_email(email: List[EmailStr], subject: str, html_content: str):
    """
    Sends an email using fastapi-mail.
    """
    message = MessageSchema(
        subject=subject,
        recipients=email,
        body=html_content,
        subtype=MessageType.html
    )
    await fm.send_message(message)

def create_verification_email_html(token: str) -> str:
    """
    Creates the HTML content for the verification email.
    """
    # In a real app, you'd use a proper HTML template engine like Jinja2
    verification_url = f"http://localhost:5173/verify-email?token={token}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #333;">Welcome to Agrotique Garden Planner!</h2>
        <p>Thank you for registering. Please click the button below to verify your email address and activate your account.</p>
        <p style="text-align: center;">
            <a href="{verification_url}" style="background-color: #28a745; color: white; padding: 15px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-size: 16px;">Verify Your Email</a>
        </p>
        <p>If you cannot click the button, please copy and paste the following link into your browser:</p>
        <p><a href="{verification_url}">{verification_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <hr>
        <p style="font-size: 12px; color: #777;">If you did not create an account, no further action is required.</p>
    </body>
    </html>
    """
    return html_content

async def send_verification_email(email_to: EmailStr, token: str):
    """
    Sends the verification email to a new user.
    """
    subject = "Verify Your Email for Agrotique Garden Planner"
    html_content = create_verification_email_html(token)
    await send_email([email_to], subject, html_content)

def create_password_reset_email_html(token: str) -> str:
    """
    Creates the HTML content for the password reset email.
    """
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #333;">Password Reset Request</h2>
        <p>You requested a password reset for your Agrotique Garden Planner account. Please click the button below to set a new password.</p>
        <p style="text-align: center;">
            <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 15px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-size: 16px;">Reset Your Password</a>
        </p>
        <p>If you cannot click the button, please copy and paste the following link into your browser:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <hr>
        <p style="font-size: 12px; color: #777;">If you did not request a password reset, you can safely ignore this email.</p>
    </body>
    </html>
    """
    return html_content

async def send_password_reset_email(email_to: EmailStr, token: str):
    """
    Sends a password reset email to a user.
    """
    subject = "Password Reset for Agrotique Garden Planner"
    html_content = create_password_reset_email_html(token)
    await send_email([email_to], subject, html_content)


class EmailService:
    """Email service wrapper for easier testing and dependency injection."""
    
    async def send_verification_email(self, email_to: str, token: str):
        """Send verification email."""
        await send_verification_email(email_to, token)
    
    async def send_password_reset_email(self, email_to: str, token: str):
        """Send password reset email."""
        await send_password_reset_email(email_to, token)


# Global email service instance
email_service = EmailService()
