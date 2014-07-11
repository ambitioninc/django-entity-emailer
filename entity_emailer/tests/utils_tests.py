from django.test import TestCase
from django_dynamic_fixture import G
from entity_subscription.models import Medium, Source

from entity_emailer.models import EmailTemplate
from entity_emailer.utils import get_medium, get_admin_source, get_admin_template


class GetMediumTest(TestCase):
    def test_get_medium_default(self):
        medium_default_name = 'email'
        G(Medium, name=medium_default_name)
        medium = get_medium()
        self.assertEqual(medium.name, medium_default_name)

    def test_get_medium_configured(self):
        custom_medium_name = 'test-email'
        G(Medium, name=custom_medium_name)
        with self.settings(ENTITY_EMAILER_MEDIUM_NAME=custom_medium_name):
            medium = get_medium()
        self.assertEqual(medium.name, custom_medium_name)


class GetAdminSourceTest(TestCase):
    def test_get_admin_source_default(self):
        admin_source_default_name = 'admin'
        G(Source, name=admin_source_default_name)
        admin_source = get_admin_source()
        self.assertEqual(admin_source.name, admin_source_default_name)

    def test_get_admin_source_configured(self):
        custom_admin_source_name = 'test-admin'
        G(Source, name=custom_admin_source_name)
        with self.settings(ENTITY_EMAILER_ADMIN_SOURCE_NAME=custom_admin_source_name):
            admin_source = get_admin_source()
        self.assertEqual(admin_source.name, custom_admin_source_name)


class GetAdminTemplateTest(TestCase):
    def test_get_admin_template_default(self):
        admin_template_default_name = 'html_safe'
        G(EmailTemplate, template_name=admin_template_default_name, html_template='<html>hi</html>')
        admin_template = get_admin_template()
        self.assertEqual(admin_template.template_name, admin_template_default_name)

    def test_get_admin_template_configured(self):
        custom_admin_template_name = 'test-template'
        G(EmailTemplate, template_name=custom_admin_template_name, html_template='<html>hi</html>')
        with self.settings(ENTITY_EMAILER_ADMIN_TEMPLATE_NAME=custom_admin_template_name):
            admin_template = get_admin_template()
        self.assertEqual(admin_template.template_name, custom_admin_template_name)
