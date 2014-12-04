from django.conf import settings
from django.core.management import BaseCommand
from entity_event.models import Medium


class Command(BaseCommand):
    def handle(self, *args, **options):
        email_medium_name = getattr(settings, 'ENTITY_EMAILER_MEDIUM_NAME', 'email')
        Medium.objects.get_or_create(
            name=email_medium_name,
            display_name=email_medium_name,
            description='Email',
        )
