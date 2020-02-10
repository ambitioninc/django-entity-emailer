import sys
import traceback

from datetime import datetime

from django.core import mail
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer.signals import pre_send, email_exception

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

        # Get the emails that we need to send
        current_time = datetime.utcnow()
        email_medium = get_medium()
        to_send = Email.objects.filter(
            scheduled__lte=current_time,
            sent__isnull=True
        ).select_related(
            'event__source'
        ).prefetch_related(
            'recipients'
        ).order_by(
            'scheduled',
            'id'
        )

        # Fetch the contexts of every event so that they may be rendered
        context_loader.load_contexts_and_renderers([e.event for e in to_send], [email_medium])

        # Keep track of what emails we will be sending
        emails = []

        # Loop over each email and generate the recipients, and message
        # and handle any exceptions that may occur
        for email in to_send:
            # Compute what email addresses we actually want to send this email to
            to_email_addresses = get_subscribed_email_addresses(email)

            # If there are no recipients we can just skip rendering
            if not to_email_addresses:
                continue

            # If any exceptions occur we will catch the exception and store it as a reference
            # As well as fire off a signal with the error and mark the email as sent and errored
            try:
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
            except Exception as e:
                # Save the exception on the model
                email.exception = traceback.format_exc()
                email.save(update_fields=['exception'])

                # Fire the email exception event
                email_exception.send(
                    sender=Email,
                    email=email,
                    exception=e
                )

        # Send all the emails that were generated properly
        connection = mail.get_connection()
        connection.send_messages(emails)

        # Update the emails as sent
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
