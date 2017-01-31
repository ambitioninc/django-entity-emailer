from bs4 import BeautifulSoup
from django.conf import settings
from django.core import mail
from entity_event.models import Medium, Source


constants = {
    'default_medium_name': 'email',
    'default_admin_source_name': 'admin',
}


def get_medium():
    """Get the medium object that the emailer associates with itself.
    """
    email_medium_name = getattr(
        settings, 'ENTITY_EMAILER_MEDIUM_NAME', constants['default_medium_name']
    )
    email_medium = Medium.objects.get(name=email_medium_name)
    return email_medium


def get_admin_source():
    """Get the source object for emails sent from the admin site.
    """
    admin_source_name = getattr(
        settings, 'ENTITY_EMAILER_ADMIN_SOURCE_NAME', constants['default_admin_source_name']
    )
    admin_source = Source.objects.get(name=admin_source_name)
    return admin_source


def get_from_email_address():
    """
    Get a 'from' address based on the django settings.
    """
    return getattr(settings, 'ENTITY_EMAILER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)


def get_subscribed_email_addresses(email):
    """
    Given the email recipients, get the email address from the entity metadata.

    The email field is determined in the settings by the ENTITY_EMAILER_EMAIL_KEY field.

    If the user wishes to exclude certain entities from receiving emails, they can define
    which field in the entity metadata to use with the EXCLUDE_ENTITY_EMAILER_KEY field.
    """

    # Get the key to use to find the email address
    email_key = getattr(settings, 'ENTITY_EMAILER_EMAIL_KEY', 'email')

    # Get the exclude key
    exclude_entity_key = getattr(settings, 'ENTITY_EMAILER_EXCLUDE_KEY', None)

    # Get the email addresses from the recipient entities
    email_addresses = []
    for entity in email.recipients.all():
        # Get the email address out of the entity meta data
        email_address = entity.entity_meta.get(email_key, None)

        # Make sure the email address exists and is not an empty string
        if email_address is not None and len(email_address):
            # If the exclude entity key is not set, or is set but the value is not none
            if not exclude_entity_key or entity.entity_meta.get(exclude_entity_key, None) is not None:
                email_addresses.append(email_address)

    # Return the email addresses
    return email_addresses


def create_email_message(to_emails, from_email, subject, text, html):
    """
    Create the appropriate plaintext or html email object.

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


def extract_email_subject_from_html_content(email_content):
    """
    This function extracts an email subject from the rendered html email context.
    It first tries to find a title block inside of a head block. If that exists,
    the title is used as the subject of the email. If it does not exist,
    the first 40 characters of the email are used as the subject. In the latter
    case, it is assumed that html tags are not actually present in the html content.
    """
    soup = BeautifulSoup(email_content)
    subject = soup.title.string.strip() if soup.title else None
    if not subject:
        subject = email_content.split('\n')[0].strip()[:40]
        if len(subject) == 40:
            subject = u'{}...'.format(subject)

    return subject
