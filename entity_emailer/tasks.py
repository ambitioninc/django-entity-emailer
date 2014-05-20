from celery import Task
from django.core.mail import send_mail
from django.template import Context, Template

from entity_emailer.models import Unsubscribed


class SendEmailAsyncNow(Task):
    def run(*args, **kwargs):
        email = kwargs.get('email')
        to_email_addresses = get_email_addresses(email)
        html_message = get_html_message(email)
        send_mail(
            subject=email.subject,
            message=html_message,
            from_email='TODO.IMPORT.THIS.FROM.SOME.TYPE.OF.SETTING@example.com',
            recipient_list=to_email_addresses,
            html_message=html_message,
        )


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
    dont_send_to = Unsubscribed.objects.filter(unsubscribed_from=email.email_type)
    send_to = set(all_entities) - set(unsub.user for unsub in dont_send_to)
    emails = [e.entity_meta['email'] for e in send_to]
    return emails


def get_html_message(email):
    """Load and render the template.

    Returns:
      A string containing the HTML email message, with the context provided
      in the email object.
    """
    with open(email.template_path) as message_template_file:
        message_template = Template(message_template_file.read())
    return message_template.render(Context(email.context))
