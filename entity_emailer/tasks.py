from datetime import datetime
import logging

from bs4 import BeautifulSoup
from celery import Task
from db_mutex.db_mutex import db_mutex
from django.conf import settings
from django.core import mail
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer.utils import get_medium

LOG = logging.getLogger(__name__)


def extract_email_subject_from_html_content(email_content):
    """
    This function extracts an email subject from the rendered html email context.
    It first tries to find a title block inside of a head block. If that exists,
    the title is used as the subject of the email. If it does not exist,
    the first 40 characters of the email are used as the subject. In the latter
    case, it is assumed that html tags are not actually present in the html content.
    """
    soup = BeautifulSoup(email_content)
    subject = soup.title.string.strip() if soup.title else None
    if not subject:
        subject = email_content.split('\n')[0].strip()[:40]
        if len(subject) == 40:
            subject = u'{}...'.format(subject)

    return subject


class SendUnsentScheduledEmails(Task):
    """
    Send all unsent emails, whose scheduled time has passed.

    This task should be added to a celery beat.
    """
    def run(self, *args, **kwargs):
        with db_mutex('send-unsent-scheduled-emails'):
            self.run_worker(*args, **kwargs)

    def run_worker(self, *args, **kwargs):
        current_time = datetime.utcnow()
        email_medium = get_medium()
        to_send = Email.objects.filter(
            scheduled__lte=current_time, sent__isnull=True).select_related('event').prefetch_related('recipients')

        # Fetch the contexts of every event so that they may be rendered
        context_loader.load_contexts_and_renderers([e.event for e in to_send], [email_medium])

        default_from_email = get_from_email_address()
        emails = []
        for email in to_send:
            to_email_addresses = get_subscribed_email_addresses(email)
            if to_email_addresses:
                text_message, html_message = email.render(email_medium)
                message = create_email_message(
                    to_emails=to_email_addresses,
                    from_email=email.from_address or default_from_email,
                    subject=email.subject or extract_email_subject_from_html_content(html_message),
                    text=text_message,
                    html=html_message,
                )
                emails.append(message)

        connection = mail.get_connection()
        connection.send_messages(emails)
        to_send.update(sent=current_time)


def create_email_message(to_emails, from_email, subject, text, html):
    """
    Create the appropriate plaintext or html email object.

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
    """
    Get a 'from' address based on the django settings.
    """
    return getattr(settings, 'ENTITY_EMAILER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)


def get_subscribed_email_addresses(email):
    """
    Given the email recipients, get the email address from the entity metadata.

    The email field is determined in the settings by the ENTITY_EMAILER_EMAIL_KEY field.

    If the user wishes to exclude certain entities from receiving emails, they can define
    which field in the entity metadata to use with the EXCLUDE_ENTITY_EMAILER_KEY field.
    """

    # Get the key to use to find the email address
    email_key = getattr(settings, 'ENTITY_EMAILER_EMAIL_KEY', 'email')

    # Get the exclude key
    exclude_entity_key = getattr(settings, 'ENTITY_EMAILER_EXCLUDE_KEY', None)

    # Get the email addresses from the recipient entities
    email_addresses = []
    for entity in email.recipients.all():
        # Get the email address out of the entity meta data
        email_address = entity.entity_meta.get(email_key, None)

        # Make sure the email address exists and is not an empty string
        if email_address is not None and len(email_address):
            # If the exclude entity key is not set, or is set but the value is not none
            if not exclude_entity_key or entity.entity_meta.get(exclude_entity_key, None) is not None:
                email_addresses.append(email_address)

    # Return the email addresses
    return email_addresses


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
        Email.objects.create_email(event=event, recipients=targets)
