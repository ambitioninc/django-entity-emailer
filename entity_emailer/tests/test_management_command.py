from django.core.management import call_command
from django.test import TestCase
from entity_event.models import Medium, Source

from entity_emailer.utils import get_medium, get_admin_source


class AddEmailMediumCommandTest(TestCase):
    def test_idempotent(self):
        call_command('add_email_medium')
        call_command('add_email_medium')
        self.assertEqual(Medium.objects.count(), 1)

    def test_default(self):
        call_command('add_email_medium')
        medium = get_medium()
        self.assertEqual(medium.name, 'email')

    def test_custom(self):
        custom_medium_name = 'test-email'
        with self.settings(ENTITY_EMAILER_MEDIUM_NAME=custom_medium_name):
            call_command('add_email_medium')
            medium = get_medium()
        self.assertEqual(medium.name, custom_medium_name)


class EntityEmailerAdminSetupTest(TestCase):
    def test_idempotent(self):
        call_command('entity_emailer_admin_setup')
        call_command('entity_emailer_admin_setup')
        self.assertEqual(Source.objects.count(), 1)

    def test_defaults(self):
        call_command('entity_emailer_admin_setup')
        source = get_admin_source()
        self.assertEqual(source.name, 'admin')

    def test_custom_source(self):
        custom_source_name = 'test-email'
        with self.settings(ENTITY_EMAILER_ADMIN_SOURCE_NAME=custom_source_name):
            call_command('entity_emailer_admin_setup')
            source = get_admin_source()
        self.assertEqual(source.name, custom_source_name)
