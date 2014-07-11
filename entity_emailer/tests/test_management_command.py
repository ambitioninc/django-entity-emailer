from django.core.management import call_command
from django.test import TestCase
from entity_subscription.models import Medium, Source

from entity_emailer import get_medium, get_admin_source, get_admin_template
from entity_emailer.models import EmailTemplate


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
        self.assertEqual(EmailTemplate.objects.count(), 1)

    def test_defaults(self):
        call_command('entity_emailer_admin_setup')
        source = get_admin_source()
        template = get_admin_template()
        self.assertEqual(source.name, 'admin')
        self.assertEqual(template.template_name, 'html_safe')

    def test_custom_source(self):
        custom_source_name = 'test-email'
        with self.settings(ENTITY_EMAILER_ADMIN_SOURCE_NAME=custom_source_name):
            call_command('entity_emailer_admin_setup')
            source = get_admin_source()
        self.assertEqual(source.name, custom_source_name)

    def test_custom_template(self):
        custom_template_name = 'test-html'
        with self.settings(ENTITY_EMAILER_ADMIN_TEMPLATE_NAME=custom_template_name):
            call_command('entity_emailer_admin_setup')
            template = get_admin_template()
        self.assertEqual(template.template_name, custom_template_name)
