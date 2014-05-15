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
    subentities = models.BooleanField()
    template_path = models.CharField(max_length=256)
    context = JSONField()
    uid = models.CharField(max_length=100, unique=True, null=True)
    scheduled = models.DateTimeField(null=True)
    sent = models.DateTimeField(null=True)


class EmailType(models.Model):
    """A broad category for emails being sent to users.

    Defining categories makes it easier for users to have some control
    over

    """
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()


class Unsubscribed(models.Model):
    """Users who have opted out of recieving certain types of email.
    """
    user = models.ForeignKey(Entity)
    unsubscribed_from = models.ForeignKey(EmailType)
