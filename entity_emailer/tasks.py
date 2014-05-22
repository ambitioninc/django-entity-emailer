from celery import Task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from entity_emailer.models import Unsubscribed


class SendEmailAsyncNow(Task):
    def run(*args, **kwargs):
        email = kwargs.get('email')
        to_email_addresses = get_email_addresses(email)
        html_message = render_to_string(email.html_template_path, email.context)
        text_message = render_to_string(email.text_template_path, email.context)
        email = EmailMultiAlternatives(
            subject=email.subject,
            body=text_message,
            to=to_email_addresses,
        )
        email.attach_alternative(html_message, 'text/html')
        email.send()


def get_email_addresses(email):
    """From an email object determine the appropriate email addresses.

    Excludes the addresses of those who unsubscribed from the email's
    type.

    Returns:
      A list of strings: email addresses.
    """
    if email.subentity_type is not None:
        all_entities = email.send_to.get_sub_entities().is_type(email.subentity_type)
    else:
        all_entities = [email.send_to]
    dont_send_to = Unsubscribed.objects.filter(
        unsubscribed_from=email.email_type).select_related('entity')
    send_to = set(all_entities) - set(unsub.entity for unsub in dont_send_to)
    emails = [e.entity_meta['email'] for e in send_to]
    return emails
