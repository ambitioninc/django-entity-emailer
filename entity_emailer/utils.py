from django.conf import settings
from entity_subscription.models import Medium


def get_medium():
    email_medium_name = getattr(settings, 'ENTITY_EMAILER_MEDIUM_NAME', 'email')
    email_medium = Medium.objects.get(name=email_medium_name)
    return email_medium
