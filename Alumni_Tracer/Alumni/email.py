from django.core.mail import send_mail
from django.conf import settings


def send_job_application_email(job_posting, applicant_name, applicant_email, cover_letter):
    subject = f'Job Application: {job_posting.job_title}'
    message = f'Dear {job_posting.company},\n\n' \
              f'I am writing to apply for the position of {job_posting.job_title} ' \
              f'at your company.\n\n' \
              f'Applicant Name: {applicant_name}\n' \
              f'Applicant Email: {applicant_email}\n\n' \
              f'Cover Letter:\n{cover_letter}\n\n' \
              f'Please consider my application.\n\n' \
              f'Thank you.\n\n' \
              f'Regards,\n{applicant_name}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [job_posting.employer.company_email]  # Assuming you have an email field in your Employer model

    send_mail(subject, message, from_email, recipient_list)
