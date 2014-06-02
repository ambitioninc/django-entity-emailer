from celery import Task
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.template import Context, Template

from entity_emailer.models import Unsubscribed


class SendEmailAsyncNow(Task):
    """Sends an email in a separate task.

    This task is spun up during the post-save signal sent when
    `entity_emailer.models.Email` objects are saved.
    """
    def run(*args, **kwargs):
        email = kwargs.get('email')
        to_email_addresses = get_email_addresses(email)
        text_message, html_message = render_templates(email)
        from_email = get_from_email_address()
        email = create_email_object(
            to_emails=to_email_addresses,
            from_email=from_email,
            subject=email.subject,
            text=text_message,
            html=html_message,
        )
        email.send()


def create_email_object(to_emails, from_email, subject, text, html):
    """Create the appropriate plaintext or html email object.

    Returns:

       email - an instance of either `django.core.mail.EmailMessage` or
       `django.core.mail.EmailMulitiAlternatives` based on whether or
       not `html_message` is empty.
    """
    if not html:
        email = mail.EmailMessage(
            subject=subject,
            body=text,
            to=to_emails,
            from_email=from_email,
        )
    else:
        email = mail.EmailMultiAlternatives(
            subject=subject,
            body=text,
            to=to_emails,
            from_email=from_email,
        )
        email.attach_alternative(html, 'text/html')
    return email


def get_from_email_address():
    """Get a 'from' address based on the django settings.
    """
    try:
        from_email = settings.ENTITY_EMAILER_FROM_EMAIL
    except AttributeError:
        from_email = settings.DEFAULT_FROM_EMAIL
    return from_email


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
    dont_send_to = frozenset(
        Unsubscribed.objects.filter(unsubscribed_from=email.email_type).values_list('entity', flat=True)
    )
    send_to = (e for e in all_entities if e.id not in dont_send_to)
    emails = [e.entity_meta['email'] for e in send_to]
    return emails


def render_templates(email):
    """Render the correct templates with the correct context.

    Args:
      An email object. Contains references to template and context.

    Returns:
      A tuple of (rendered_text, rendered_html). Either, but not both
      may be an empty string.
    """
    # Process text template:
    if email.template.text_template_path:
        rendered_text = render_to_string(
            email.template.text_template_path, email.context
        )
    elif email.template.text_template:
        context = Context(email.context)
        rendered_text = Template(email.template.text_template).render(context)
    else:
        rendered_text = ''

    # Process html template
    if email.template.html_template_path:
        rendered_html = render_to_string(
            email.template.text_template_path, email.context
        )
    elif email.template.html_template:
        context = Context(email.context)
        rendered_html = Template(email.template.html_template).render(context)
    else:
        rendered_html = ''

    return (rendered_text, rendered_html)
