from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from entity.models import Entity
from jsonfield import JSONField


class Email(models.Model):
    """Save an Email object and it is sent automagically!

    If an Email object is saved without a `scheduled` time, it will
    immediately and automatically be sent.

    If an Email object is saved with a `scheduled` time, it will be
    sent at that time.

    Emails can be sent to an individual, by setting subentities to
    False, or to a group, by setting send_to to a superentity, like a
    Team or Organization, and setting subentities to True.

    Sending an email happens automatically, and consists of rendering
    the given template with the given context
    """
    email_type = models.ForeignKey('EmailType')
    send_to = models.ForeignKey(Entity)
    subentity_type = models.ForeignKey(ContentType, null=True, default=None)
    subject = models.CharField(max_length=256)
    template = models.ForeignKey('EmailTemplate')
    context = JSONField()
    uid = models.CharField(max_length=100, unique=True, null=True, default=None)
    scheduled = models.DateTimeField(null=True, default=None)
    sent = models.DateTimeField(null=True, default=None)


class EmailTemplate(models.Model):
    """A template for email to be sent. Rendered by django with context.

    Of the four fields: `text_template_path`, 'html_template_path',
    `text_template`, and `html_template`, at least one must be
    non-empty.

    Both a text and html template may be provided, either
    through a path to the template, or a raw template object.

    However, for either text or html templates, both a path and raw
    template should not be provided.

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


class EmailType(models.Model):
    """A broad category for emails being sent to users.

    Defining categories makes it easier for users to have some control
    over
    """
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()


class Unsubscribed(models.Model):
    """Entities (users) who have opted out of recieving types of email.
    """
    entity = models.ForeignKey(Entity)
    unsubscribed_from = models.ForeignKey(EmailType)


# Register the email save handler. This must be done at the end of the
# file to avoid a circular import.
from entity_emailer import handlers

# make flake8 happy
assert handlers
