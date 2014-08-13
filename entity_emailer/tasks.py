from datetime import datetime

from celery import Task
from db_mutex import db_mutex
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.template import Context, Template
from entity_subscription.models import Subscription

from entity_emailer.models import Email
from entity_emailer import get_medium


class SendUnsentScheduledEmails(Task):
    """Send all unsent emails, whose scheduled time has passed.

    This task should be added to a celery beat.
    """
    def run(self, *args, **kwargs):
        with db_mutex('send-unsent-scheduled-emails'):
            self.run_worker(*args, **kwargs)

    def run_worker(self, *args, **kwargs):
        current_time = datetime.utcnow()
        to_send = Email.objects.filter(scheduled__lte=current_time, sent__isnull=True)
        default_from_email = get_from_email_address()
        emails = []
        for email in to_send:
            to_email_addresses = get_subscribed_email_addresses(email)
            text_message, html_message = render_templates(email)
            message = create_email_message(
                to_emails=to_email_addresses,
                from_email=email.from_address or default_from_email,
                subject=email.subject,
                text=text_message,
                html=html_message,
            )
            emails.append(message)
        connection = mail.get_connection()
        connection.send_messages(emails)
        to_send.update(sent=current_time)


def create_email_message(to_emails, from_email, subject, text, html):
    """Create the appropriate plaintext or html email object.

    Returns:

       email - an instance of either `django.core.mail.EmailMessage` or
       `django.core.mail.EmailMulitiAlternatives` based on whether or
       not `html_message` is empty.
    """
    if not html:
        email = mail.EmailMessage(
            subject=subject,
            body=text,
            to=to_emails,
            from_email=from_email,
        )
    else:
        email = mail.EmailMultiAlternatives(
            subject=subject,
            body=text,
            to=to_emails,
            from_email=from_email,
        )
        email.attach_alternative(html, 'text/html')
    return email


def get_from_email_address():
    """Get a 'from' address based on the django settings.
    """
    return getattr(settings, 'ENTITY_EMAILER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)


def get_subscribed_email_addresses(email):
    """From an email object determine the appropriate email addresses.

    Excludes the addresses of those who unsubscribed from the email's
    type.

    Returns:
      A list of strings: email addresses.
    """
    email_medium = get_medium()
    if email.subentity_type is not None:
        all_entities = list(email.send_to.get_sub_entities().is_any_type(email.subentity_type))
    else:
        all_entities = [email.send_to]
    send_to = Subscription.objects.filter_not_subscribed(
        source=email.source, medium=email_medium, entities=all_entities
    )
    emails = [e.entity_meta['email'] for e in send_to]
    return emails


def render_templates(email):
    """Render the correct templates with the correct context.

    Args:
      An email object. Contains references to template and context.

    Returns:
      A tuple of (rendered_text, rendered_html). Either, but not both
      may be an empty string.
    """
    # Process text template:
    if email.template.text_template_path:
        rendered_text = render_to_string(
            email.template.text_template_path, email.context
        )
    elif email.template.text_template:
        context = Context(email.context)
        rendered_text = Template(email.template.text_template).render(context)
    else:
        rendered_text = ''

    # Process html template
    if email.template.html_template_path:
        rendered_html = render_to_string(
            email.template.html_template_path, email.context
        )
    elif email.template.html_template:
        context = Context(email.context)
        rendered_html = Template(email.template.html_template).render(context)
    else:
        rendered_html = ''

    return (rendered_text, rendered_html)
