from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from entity_emailer.models import Email


@receiver(post_save, sender=Email, dispatch_uid='handle_email_save')
def handle_email_save(sender, instance, **kwargs):
    """Spawn a task to send the email post-save.
    """
    # If the email is scheduled for later, don't proccess it in
    # post-save. It will be sent later, by the scheduler.
    if instance.scheduled is not None and instance.scheduled > datetime.utcnow():
        return

    # This import occurs here to prevent circular import errors.
    from entity_emailer.tasks import SendEmailAsyncNow
    SendEmailAsyncNow().delay(email=instance)
