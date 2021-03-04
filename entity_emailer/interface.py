from datetime import datetime
import json
import sys
import traceback

from ambition_utils.transaction import durable
from django.conf import settings
from django.core import mail
from django.db import transaction
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer.signals import pre_send, email_exception
from entity_emailer.utils import get_medium, get_from_email_address, get_subscribed_email_addresses, \
    create_email_message, extract_email_subject_from_html_content


class EntityEmailerInterface(object):
    """
    An api interface to do things within entity emailer
    """

    @classmethod
    @durable
    def send_unsent_scheduled_emails(cls):
        """
        Send out any scheduled emails that are unsent
        """

        # Get the emails that we need to send
        current_time = datetime.utcnow()
        email_medium = get_medium()
        to_send = Email.objects.filter(
            scheduled__lte=current_time,
            sent__isnull=True,
            num_tries__lt=settings.ENTITY_EMAILER_MAX_SEND_MESSAGE_TRIES
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
        emails_to_send = []

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
                emails_to_send.append({
                    'message': message,
                    'model': email,
                })
            except Exception:
                # Save the exception on the model
                cls.save_email_exception(email, traceback.format_exc())

        # Send all the emails that were generated properly
        with mail.get_connection() as connection:
            for email in emails_to_send:
                try:
                    # Send mail
                    connection.send_messages([email.get('message')])
                    # Update the email model sent value
                    email_model = email.get('model')
                    email_model.sent = current_time
                    email_model.save(update_fields=['sent'])
                except Exception as e:
                    cls.save_email_exception(email.get('model'), e)

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

    @staticmethod
    @transaction.atomic
    def bulk_convert_events_to_emails():
        """
        Converts unseen events to emails and marks them as seen. Uses the create_emails method to bulk create
        emails and recipient relationships
        """

        # Get the email medium
        email_medium = get_medium()

        # Get the default from email
        default_from_email = get_from_email_address()

        email_params_list = []

        # Find any unseen events and create unsent email objects
        for event, targets in email_medium.events_targets(seen=False, mark_seen=True):

            # Check the event's context for a from_address, otherwise fallback to default
            from_address = event.context.get('from_address') or default_from_email

            email_params_list.append(dict(
                event=event,
                from_address=from_address,
                recipients=targets
            ))

        # Bulk create the emails
        Email.objects.create_emails(email_params_list)

    @classmethod
    def save_email_exception(cls, email, e):
        # Save the error to the email model
        exception_message = str(e)

        # Duck typing exception for sendgrid api backend rather than place hard dependency
        if hasattr(e, 'to_dict'):
            exception_message += ': {}'.format(json.dumps(e.to_dict()))

        email.exception = exception_message
        email.num_tries += 1
        email.save(update_fields=['exception', 'num_tries'])

        # Fire the email exception event
        email_exception.send(
            sender=Email,
            email=email,
            exception=e
        )
