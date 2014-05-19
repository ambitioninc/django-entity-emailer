from datetime.datetime import utcnow

from django.db.models.signal import post_save
from django.dispatch import reciever

from entity_emailer.models import Email


@reciever(post_save, sender=Email, dispatch_uid='handle_email_save')
def handle_email_save(sender, **kwargs):
    email = kwargs['instance']
    # If the email is scheduled for later, don't proccess it in
    # post-save.
    if email.scheduled > utcnow():
        return

    # This import occurs here to prevent circular import errors.
    from entity_emailer.tasks import send_email_async_now
    send_email_async_now(email)
