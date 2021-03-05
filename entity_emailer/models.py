from datetime import datetime

from django.db import models, transaction
from entity.models import Entity
from entity_event.models import Event
import uuid


class EmailManager(models.Manager):
    """
    Provides the ability to easily create emails with the recipients.
    """
    def create_email(self, recipients=None, **kwargs):
        """
        Note that we pop the scheduled time from the kwargs before creating the email
        and then update the scheduled time after the recipients have been added. This
        avoids the potential race condition of the email being created before it is
        picked up by a task that sends it.
        """
        scheduled = kwargs.pop('scheduled', datetime.utcnow())
        email = Email.objects.create(scheduled=None, **kwargs)
        if recipients:
            email.recipients.add(*recipients)

        email.scheduled = scheduled
        email.save()
        return email

    @transaction.atomic
    def create_emails(self, email_params_list):
        """
        :param email_params_list: A list of dicts containing the keys for the create_email method
        :return: list of Email objects that were created
        """
        emails_to_create = []
        recipient_entities_per_email = []

        # Build the emails to create and keep track of recipients
        for kwargs in email_params_list:
            scheduled = kwargs.pop('scheduled', datetime.utcnow())
            recipients = kwargs.pop('recipients', [])
            emails_to_create.append(Email(scheduled=scheduled, **kwargs))
            recipient_entities_per_email.append(recipients)

        # Bulk create the emails
        emails = Email.objects.bulk_create(emails_to_create)

        # Build list of recipient through relationships to create
        recipients_to_create = []

        # Keep track of unique pairs to avoid unique constraint on through relationship
        email_entity_pairs = set()
        for i, recipient_entities in enumerate(recipient_entities_per_email):
            for recipient_entity in recipient_entities:
                if (emails[i].id, recipient_entity.id) not in email_entity_pairs:
                    email_entity_pairs.add((emails[i].id, recipient_entity.id))

                    recipients_to_create.append(
                        Email.recipients.through(
                            email_id=emails[i].id,
                            entity_id=recipient_entity.id,
                        )
                    )

        # Bulk create the recipient relationships
        Email.recipients.through.objects.bulk_create(recipients_to_create)

        return emails


class Email(models.Model):
    """Save an Email object and it is sent automagically!

    If an Email object is saved without a `scheduled` time, it will
    immediately and automatically be sent.

    If an Email object is saved with a `scheduled` time, it will be
    sent at that time.

    Emails can be sent to an individual, by setting subentities to
    False, or to a group, by setting send_to to a superentity, like a
    Team or Organization, and setting subentities to True. This applies
    to every entity in the recipients list.

    Sending an email happens automatically, and consists of rendering
    the given template with the given context.

    Emails will not be sent to any individual who has unsubscribed
    from emails of that source.

    Emails are viewable online and identified with their view_uid UUID
    """
    view_uid = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Entity)
    subject = models.CharField(max_length=256)
    from_address = models.CharField(max_length=256, default='')
    uid = models.CharField(max_length=100, unique=True, null=True, default=None)
    # The `scheduled` field uses a default value of the datetime.utcnow function.
    # This means it will be called any time a new Email is created, but it also
    # allows for a different schedule to be set (to schedule the email for some
    # time in the future), which would not be possible with an auto_add_now=True.
    scheduled = models.DateTimeField(null=True, default=datetime.utcnow)

    # The time that the email was actually sent, or None if the email is still waiting to be sent
    sent = models.DateTimeField(null=True, default=None)

    # Number of attempts to send this email message, used only in retry logic
    num_tries = models.IntegerField(default=0)

    # Any exception that occurred when attempting to send the email last
    exception = models.TextField(default=None, null=True)

    objects = EmailManager()

    def render(self, medium):
        """
        Renders the event, assuming it has already had its context and renderers prefetched.
        """
        self.event.context['entity_emailer_id'] = str(self.view_uid)
        return self.event.render(medium)
