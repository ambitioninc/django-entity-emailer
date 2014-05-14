
from django.db import models
from entity.models import Entity
from jsonfield import JSONField

class Email(models.Model):
    email_type = models.ForeignKey(EmailType)
    send_to = models.ForeignKey(Entity)
    subentities = models.BooleanField()
    template = models.TextField()
    context = JSONField()
    uid = models.CharField(max_length=100, unique=True, null=True)
    scheduled = models.DateTimeField(null=True)
    sent = models.DateTimeField(null=True)
