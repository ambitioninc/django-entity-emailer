from django.conf import settings
from django.core.management import BaseCommand
from entity_event.models import Source, SourceGroup

from entity_emailer.utils import constants


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin_source_name = getattr(
            settings, 'ENTITY_EMAILER_ADMIN_SOURCE_NAME', constants['default_admin_source_name']
        )
        source_group = SourceGroup.objects.get_or_create(
            name=admin_source_name,
            defaults={
                'display_name': admin_source_name,
                'description': 'Admin notifications.',
            }
        )[0]
        Source.objects.get_or_create(
            name=admin_source_name,
            defaults={
                'group': source_group,
                'display_name': admin_source_name,
                'description': 'Admin notifications.',
            })
