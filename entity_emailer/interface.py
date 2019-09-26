import sys

from datetime import datetime

from django.core import mail
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer.signals import pre_send

from entity_emailer.utils import get_medium, get_from_email_address, get_subscribed_email_addresses, \
    create_email_message, extract_email_subject_from_html_content


class EntityEmailerInterface(object):
    """
    An api interface to do things within entity emailer
    """

    @staticmethod
    def send_unsent_scheduled_emails():
        """
        Send out any scheduled emails that are unsent
        """

        current_time = datetime.utcnow()
        email_medium = get_medium()
        to_send = Email.objects.filter(
            scheduled__lte=current_time,
            sent__isnull=True
        ).select_related(
            'event__source'
        ).prefetch_related(
            'recipients'
        )

        # Fetch the contexts of every event so that they may be rendered
        context_loader.load_contexts_and_renderers([e.event for e in to_send], [email_medium])

        emails = []
        for email in to_send:
            to_email_addresses = get_subscribed_email_addresses(email)
            if to_email_addresses:
                # Render the email
                text_message, html_message = email.render(email_medium)

                # Create the email
                message = create_email_message(
                    to_emails=to_email_addresses,
                    from_email=email.from_address or get_from_email_address(),
                    subject=email.subject or extract_email_subject_from_html_content(html_message),
                    text=text_message,
                    html=html_message,
                )

                # Fire the pre send signal
                pre_send.send(
                    sender=sys.intern(email.event.source.name),
                    email=email,
                    event=email.event,
                    context=email.event.context,
                    message=message,
                )

                # Add the email to the list of emails that need to be sent
                emails.append(message)

        connection = mail.get_connection()
        connection.send_messages(emails)
        to_send.update(sent=current_time)

    @staticmethod
    def convert_events_to_emails():
        """
        Converts unseen events to emails and marks them as seen.
        """

        # Get the email medium
        email_medium = get_medium()

        # Get the default from email
        default_from_email = get_from_email_address()

        # Find any unseen events and create unsent email objects
        for event, targets in email_medium.events_targets(seen=False, mark_seen=True):

            # Check the event's context for a from_address, otherwise fallback to default
            from_address = event.context.get('from_address') or default_from_email

            # Create the emails
            Email.objects.create_email(event=event, from_address=from_address, recipients=targets)
