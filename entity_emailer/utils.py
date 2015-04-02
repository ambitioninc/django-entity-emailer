from django.conf import settings
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
