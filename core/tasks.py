from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from core.models import Case, RejectedCase
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_case_approved_email(case_id):
    """Send email to client when case is approved"""
    try:
        case = Case.objects.get(id=case_id)
        client_email = case.client.email
        client_name = case.client.first_name or case.client.username

        subject = f"Your Case Has Been Approved - Case #{case.case_number}"
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Case Approval Notification</h2>
                <p>Dear {client_name},</p>
                <p>We are pleased to inform you that your case has been approved.</p>
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                    <p><strong>Case Details:</strong></p>
                    <p><strong>Case Number:</strong> {case.case_number}</p>
                    <p><strong>Case Title:</strong> {case.title}</p>
                    <p><strong>Case Type:</strong> {case.case_type}</p>
                    <p><strong>Amount Involved:</strong> ${case.amount_involved}</p>
                    <p><strong>Registration Fee:</strong> ${case.registration_fee}</p>
                    <p><strong>Assigned Lawyer:</strong> {case.lawyer.first_name or case.lawyer.username}</p>
                </div>
                <p>Your case has been assigned to our lawyer who will contact you shortly with next steps.</p>
                <p>Thank you for choosing our legal management system.</p>
                <p>Best regards,<br>Lawsuit Management System</p>
            </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Approval email sent to {client_email} for case {case.case_number}")
        return f"Email sent successfully to {client_email}"
    
    except Exception as e:
        logger.error(f"Error sending approval email for case {case_id}: {str(e)}")
        raise


@shared_task
def send_case_rejected_email(rejected_case_id):
    """Send email to client when case is rejected"""
    try:
        rejected_case = RejectedCase.objects.get(id=rejected_case_id)
        client_email = rejected_case.client.email
        client_name = rejected_case.client.first_name or rejected_case.client.username

        subject = f"Case Request Status - Your Case Has Been Rejected"
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Case Rejection Notification</h2>
                <p>Dear {client_name},</p>
                <p>We regret to inform you that your case request has been rejected after careful review.</p>
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                    <p><strong>Case Details:</strong></p>
                    <p><strong>Case Title:</strong> {rejected_case.title}</p>
                    <p><strong>Case Type:</strong> {rejected_case.case_type}</p>
                    <p><strong>Rejection Reason:</strong></p>
                    <p style="font-style: italic;">{rejected_case.rejection_reason}</p>
                </div>
                <p>If you have any questions or would like to discuss this decision, please feel free to contact us.</p>
                <p>We appreciate your interest and hope to assist you in the future.</p>
                <p>Best regards,<br>Lawsuit Management System</p>
            </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Rejection email sent to {client_email} for case {rejected_case.title}")
        return f"Email sent successfully to {client_email}"
    
    except Exception as e:
        logger.error(f"Error sending rejection email for rejected case {rejected_case_id}: {str(e)}")
        raise


@shared_task
def send_payment_reminder_email(case_id):
    """Send payment reminder to client"""
    try:
        case = Case.objects.get(id=case_id)
        if not case.registration_fee_paid:
            client_email = case.client.email
            client_name = case.client.first_name or case.client.username

            subject = f"Payment Reminder - Case #{case.case_number}"
            
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Payment Reminder</h2>
                    <p>Dear {client_name},</p>
                    <p>This is a friendly reminder that your case registration fee is pending.</p>
                    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                        <p><strong>Case Number:</strong> {case.case_number}</p>
                        <p><strong>Registration Fee:</strong> ${case.registration_fee}</p>
                    </div>
                    <p>Please complete your payment to proceed with your case processing.</p>
                    <p>Thank you!</p>
                </body>
            </html>
            """
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Payment reminder sent to {client_email} for case {case.case_number}")
    
    except Exception as e:
        logger.error(f"Error sending payment reminder for case {case_id}: {str(e)}")
