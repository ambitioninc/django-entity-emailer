from datetime import datetime
import logging

from celery import Task
from db_mutex import db_mutex
from django.conf import settings
from django.core import mail
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer import get_medium

LOG = logging.getLogger(__name__)


class SendUnsentScheduledEmails(Task):
    """Send all unsent emails, whose scheduled time has passed.

    This task should be added to a celery beat.
    """
    def run(self, *args, **kwargs):
        with db_mutex('send-unsent-scheduled-emails'):
            self.run_worker(*args, **kwargs)

    def run_worker(self, *args, **kwargs):
        current_time = datetime.utcnow()
        email_medium = get_medium()
        to_send = Email.objects.filter(scheduled__lte=current_time, sent__isnull=True).select_related('event')

        # Fetch the contexts of every event so that they may be rendered
        context_loader.load_contexts_and_renderers([e.event for e in to_send], [email_medium])

        default_from_email = get_from_email_address()
        emails = []
        for email in to_send:
            to_email_addresses = get_subscribed_email_addresses(email)
            text_message, html_message = email.event.render(email_medium)
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
    if email.sub_entity_kind is not None:
        all_entities = [
            se
            for recipient in email.recipients.all()
            for se in recipient.get_sub_entities() if se.entity_kind_id == email.sub_entity_kind_id
        ]
    else:
        all_entities = list(email.recipients.all())

    send_to = email_medium.filter_source_targets_by_unsubscription(email.source_id, all_entities)
    emails = [e.entity_meta['email'] for e in send_to]
    return emails


class ConvertEventsToEmails(Task):
    """
    Converts events to emails based on the email subscriptions.
    """
    def run(self, *args, **kwargs):
        with db_mutex('convert-events-to-emails'):
            self.run_worker(*args, **kwargs)

    def run_worker(self, *args, **kwargs):
        convert_events_to_emails()


def convert_events_to_emails():
    """
    Converts unseen events to emails and marks them as seen.
    """
    email_medium = get_medium()

    for event, targets in email_medium.events_targets(seen=False, mark_seen=True):
        # TODO Update this so that it inspects the rendered email itself to determine the subject
        # or figure out a solution so that the subject is determined dynamically from the email
        # content
        Email.objects.create_email(
            event=event, recipients=targets, subject=event.context.get('entity_emailer_subject', 'Email'))
