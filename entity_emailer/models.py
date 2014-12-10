from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from entity.models import Entity, EntityKind
from entity_event.models import Source
from jsonfield import JSONField


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
    """
    source = models.ForeignKey(Source)
    sub_entity_kind = models.ForeignKey(EntityKind, null=True, default=None)
    recipients = models.ManyToManyField(Entity)
    subject = models.CharField(max_length=256)
    from_address = models.CharField(max_length=256, default='')
    template = models.ForeignKey('EmailTemplate')
    context = JSONField()
    uid = models.CharField(max_length=100, unique=True, null=True, default=None)
    # The `scheduled` field uses a default value of the datetime.utcnow function.
    # This means it will be called any time a new Email is created, but it also
    # allows for a different schedule to be set (to schedule the email for some
    # time in the future), which would not be possible with an auto_add_now=True.
    scheduled = models.DateTimeField(null=True, default=datetime.utcnow)
    sent = models.DateTimeField(null=True, default=None)

    objects = EmailManager()

    def get_context(self):
        """
        Retrieves the context for this email, passing it through the context loader of
        the email template if necessary. It also adds the email url address to the context.
        """
        context = self.source.get_context(self.context)
        context['entity_emailer_id'] = self.id
        return context


class EmailTemplate(models.Model):
    """A template for email to be sent. Rendered by django with context.

    Of the four fields: `text_template_path`, 'html_template_path',
    `text_template`, and `html_template`, at least one must be
    non-empty.

    Both a text and html template may be provided, either
    through a path to the template, or a raw template object.

    However, for either text or html templates, both a path and raw
    template should not be provided.

    For more complex context loading capabilities, provide an executable
    function for loading the email context. This function accepts the
    context stored for the email and returns the context again with any
    other fetched values.

    The email sending task will take care of rendering the template,
    and creating a text or text/html message based on the rendered
    template.
    """
    template_name = models.CharField(max_length=64, unique=True)
    text_template_path = models.CharField(max_length=256, default='')
    html_template_path = models.CharField(max_length=256, default='')
    text_template = models.TextField(default='')
    html_template = models.TextField(default='')

    def clean(self):
        template_fields = [
            self.text_template_path, self.html_template_path,
            self.text_template, self.html_template
        ]
        if not any(template_fields):
            raise ValidationError('At least one template source must be provided')
        if self.text_template_path and self.text_template:
            raise ValidationError('Cannot provide a template path and template')
        if self.html_template_path and self.html_template:
            raise ValidationError('Cannot provide a template path and template')

    def save(self, *args, **kwargs):
        self.clean()
        super(EmailTemplate, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.template_name


class IndividualEmailManager(models.Manager):
    def get_queryset(self):
        return super(IndividualEmailManager, self).get_queryset().filter(sub_entity_kind__isnull=True)


class IndividualEmail(Email):
    """A proxy model of Email to support a different admin Interface.
    """
    class Meta:
        proxy = True

    objects = IndividualEmailManager()


class GroupEmailManager(models.Manager):
    def get_queryset(self):
        return super(GroupEmailManager, self).get_queryset().filter(sub_entity_kind__isnull=False)


class GroupEmail(Email):
    """A proxy model of Email to support a different admin Interface.
    """
    class Meta:
        proxy = True

    objects = GroupEmailManager()
