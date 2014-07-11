from django.conf import settings
from django.core.management import BaseCommand
from entity_subscription.models import Source

from entity_emailer.utils import constants
from entity_emailer.models import EmailTemplate


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin_source_name = getattr(
            settings, 'ENTITY_EMAILER_ADMIN_SOURCE_NAME', constants['default_admin_source_name']
        )
        admin_template_name = getattr(
            settings, 'ENTITY_EMAILER_ADMIN_TEMPLATE_NAME', constants['default_admin_template_name']
        )
        Source.objects.get_or_create(
            name=admin_source_name,
            display_name=admin_source_name,
            description='Admin notifications.',
        )
        EmailTemplate.objects.get_or_create(
            template_name=admin_template_name,
            html_template='{{ html|safe }}',
        )
