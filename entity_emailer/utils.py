from django.conf import settings
from entity_subscription.models import Medium, Source

from entity_emailer.models import EmailTemplate


constants = {
    'default_medium_name': 'email',
    'default_admin_source_name': 'admin',
    'default_admin_template_name': 'html_safe'
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


def get_admin_template():
    """Get the EmailTemplate object for emails sent from the admin site.
    """
    admin_template_name = getattr(
        settings, 'ENTITY_EMAILER_ADMIN_TEMPLATE_NAME', constants['default_admin_template_name']
    )
    admin_template = EmailTemplate.objects.get(template_name=admin_template_name)
    return admin_template
