"""
Email service for sending transactional emails.

Supports:
- Password reset emails
- Email verification
- Welcome emails
- Document processing notifications
- Subscription notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
from pathlib import Path
from jinja2 import Template

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using SMTP for transactional emails.

    Supports HTML templates with Jinja2 and graceful degradation
    when SMTP is not configured (logs email instead).
    """

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])

        if not self.enabled:
            logger.warning("SMTP not configured. Emails will be logged instead of sent.")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(
                f"[EMAIL NOT SENT - SMTP disabled] To: {to_email}, Subject: {subject}\n"
                f"Content: {text_content or html_content[:200]}..."
            )
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add plain text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str,
    ) -> bool:
        """
        Send password reset email with reset link.

        Args:
            to_email: User's email address
            reset_token: Password reset token
            user_name: User's name

        Returns:
            True if sent successfully
        """
        # Build reset URL
        frontend_url = settings.CORS_ORIGINS.split(",")[0] if settings.CORS_ORIGINS else "http://localhost:3000"
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"

        # HTML template
        html_content = self._render_password_reset_template(
            user_name=user_name,
            reset_url=reset_url,
        )

        # Plain text fallback
        text_content = f"""
Hi {user_name},

You requested to reset your password for BuiltEnvironment.ai.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The BuiltEnvironment.ai Team
"""

        return await self.send_email(
            to_email=to_email,
            subject="Reset Your Password - BuiltEnvironment.ai",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: str,
    ) -> bool:
        """
        Send email verification link.

        Args:
            to_email: User's email address
            verification_token: Verification token
            user_name: User's name

        Returns:
            True if sent successfully
        """
        # Build verification URL
        frontend_url = settings.CORS_ORIGINS.split(",")[0] if settings.CORS_ORIGINS else "http://localhost:3000"
        verification_url = f"{frontend_url}/verify-email?token={verification_token}"

        # HTML template
        html_content = self._render_email_verification_template(
            user_name=user_name,
            verification_url=verification_url,
        )

        # Plain text fallback
        text_content = f"""
Hi {user_name},

Welcome to BuiltEnvironment.ai!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

Best regards,
The BuiltEnvironment.ai Team
"""

        return await self.send_email(
            to_email=to_email,
            subject="Verify Your Email - BuiltEnvironment.ai",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Send welcome email after successful registration.

        Args:
            to_email: User's email address
            user_name: User's name

        Returns:
            True if sent successfully
        """
        frontend_url = settings.CORS_ORIGINS.split(",")[0] if settings.CORS_ORIGINS else "http://localhost:3000"

        html_content = self._render_welcome_template(
            user_name=user_name,
            dashboard_url=f"{frontend_url}/dashboard",
        )

        text_content = f"""
Hi {user_name},

Welcome to BuiltEnvironment.ai!

Your account has been successfully created. You can now:
- Upload building documents for compliance checking
- Chat with AI specialists about UK Building Regulations
- Manage projects and track compliance findings

Get started: {frontend_url}/dashboard

Best regards,
The BuiltEnvironment.ai Team
"""

        return await self.send_email(
            to_email=to_email,
            subject="Welcome to BuiltEnvironment.ai",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_document_processed_email(
        self,
        to_email: str,
        user_name: str,
        document_name: str,
        findings_count: int,
        project_name: str,
    ) -> bool:
        """
        Notify user when document processing is complete.

        Args:
            to_email: User's email
            user_name: User's name
            document_name: Name of processed document
            findings_count: Number of compliance findings
            project_name: Project name

        Returns:
            True if sent successfully
        """
        frontend_url = settings.CORS_ORIGINS.split(",")[0] if settings.CORS_ORIGINS else "http://localhost:3000"

        html_content = self._render_document_processed_template(
            user_name=user_name,
            document_name=document_name,
            findings_count=findings_count,
            project_name=project_name,
            view_url=f"{frontend_url}/projects",
        )

        text_content = f"""
Hi {user_name},

Your document "{document_name}" has been processed successfully.

Project: {project_name}
Compliance Findings: {findings_count}

View results: {frontend_url}/projects

Best regards,
The BuiltEnvironment.ai Team
"""

        return await self.send_email(
            to_email=to_email,
            subject=f"Document Processed: {document_name}",
            html_content=html_content,
            text_content=text_content,
        )

    def _render_password_reset_template(self, user_name: str, reset_url: str) -> str:
        """Render password reset email HTML."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .footer { padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ BuiltEnvironment.ai</h1>
        </div>
        <div class="content">
            <h2>Reset Your Password</h2>
            <p>Hi {{ user_name }},</p>
            <p>You requested to reset your password. Click the button below to create a new password:</p>
            <a href="{{ reset_url }}" class="button">Reset Password</a>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
            <p>For security, never share this link with anyone.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 BuiltEnvironment.ai - AI-Powered Building Compliance</p>
        </div>
    </div>
</body>
</html>
""")
        return template.render(user_name=user_name, reset_url=reset_url)

    def _render_email_verification_template(self, user_name: str, verification_url: str) -> str:
        """Render email verification HTML."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .footer { padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ BuiltEnvironment.ai</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email</h2>
            <p>Hi {{ user_name }},</p>
            <p>Welcome to BuiltEnvironment.ai! Please verify your email address to get started:</p>
            <a href="{{ verification_url }}" class="button">Verify Email</a>
            <p><strong>This link will expire in 24 hours.</strong></p>
        </div>
        <div class="footer">
            <p>&copy; 2025 BuiltEnvironment.ai - AI-Powered Building Compliance</p>
        </div>
    </div>
</body>
</html>
""")
        return template.render(user_name=user_name, verification_url=verification_url)

    def _render_welcome_template(self, user_name: str, dashboard_url: str) -> str:
        """Render welcome email HTML."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .features { background: white; padding: 20px; margin: 20px 0; border-radius: 6px; }
        .footer { padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Welcome to BuiltEnvironment.ai</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }}!</h2>
            <p>Your account has been successfully created. Get started with AI-powered building compliance:</p>

            <div class="features">
                <h3>What you can do:</h3>
                <ul>
                    <li>📄 Upload building documents for instant compliance checking</li>
                    <li>🤖 Chat with specialist AI agents about UK Building Regulations</li>
                    <li>📊 Track compliance findings and generate reports</li>
                    <li>👥 Collaborate with your team on projects</li>
                </ul>
            </div>

            <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>

            <p>Need help? Check out our documentation or contact support.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 BuiltEnvironment.ai - AI-Powered Building Compliance</p>
        </div>
    </div>
</body>
</html>
""")
        return template.render(user_name=user_name, dashboard_url=dashboard_url)

    def _render_document_processed_template(
        self,
        user_name: str,
        document_name: str,
        findings_count: int,
        project_name: str,
        view_url: str,
    ) -> str:
        """Render document processed notification HTML."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .stats { background: white; padding: 20px; margin: 20px 0; border-radius: 6px; }
        .footer { padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Document Processed</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p>Your document has been successfully processed and analyzed:</p>

            <div class="stats">
                <p><strong>Document:</strong> {{ document_name }}</p>
                <p><strong>Project:</strong> {{ project_name }}</p>
                <p><strong>Compliance Findings:</strong> {{ findings_count }}</p>
            </div>

            <a href="{{ view_url }}" class="button">View Results</a>

            <p>The AI has analyzed your document against UK Building Regulations and identified compliance points.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 BuiltEnvironment.ai - AI-Powered Building Compliance</p>
        </div>
    </div>
</body>
</html>
""")
        return template.render(
            user_name=user_name,
            document_name=document_name,
            findings_count=findings_count,
            project_name=project_name,
            view_url=view_url,
        )


# Global email service instance
email_service = EmailService()
