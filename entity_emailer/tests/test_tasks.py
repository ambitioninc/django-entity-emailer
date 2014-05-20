from entity.models import Entity, EntityRelationship
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G, N
from mock import patch

from entity_emailer import tasks
from entity_emailer.models import Email, EmailType, Unsubscribed


class Test_get_email_addresses(TestCase):
    def setUp(self):
        self.ct = ContentType.objects.get_for_model(Email)
        self.ct2 = ContentType.objects.get_for_model(Unsubscribed)
        self.super_entity = G(Entity, entity_meta={'email': 'test_super@example.com'}, entity_type=self.ct)
        self.sub_entity_1 = G(Entity, entity_meta={'email': 'test_sub1@example.com'}, entity_type=self.ct)
        self.sub_entity_2 = G(Entity, entity_meta={'email': 'test_sub2@example.com'}, entity_type=self.ct)
        self.sub_entity_3 = G(Entity, entity_meta={'email': 'test_sub3@example.com'}, entity_type=self.ct2)
        G(EntityRelationship, sub_entity=self.sub_entity_1, super_entity=self.super_entity)
        G(EntityRelationship, sub_entity=self.sub_entity_2, super_entity=self.super_entity)
        G(EntityRelationship, sub_entity=self.sub_entity_3, super_entity=self.super_entity)

    def test_returns_sub_entities_emails(self):
        email = N(Email, send_to=self.super_entity, subentity_type=self.ct, context={})
        addresses = tasks.get_email_addresses(email)
        expected_addresses = {u'test_sub1@example.com', u'test_sub2@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_filters_other_entity_types(self):
        email = N(Email, send_to=self.super_entity, subentity_type=self.ct2, context={})
        addresses = tasks.get_email_addresses(email)
        expected_addresses = {u'test_sub3@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_returns_own_email(self):
        email = N(Email, send_to=self.super_entity, subentity_type=None, context={})
        addresses = tasks.get_email_addresses(email)
        expected_addresses = {u'test_super@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_unsubscription_works(self):
        test_email_type = G(EmailType, name='test_email')
        G(Unsubscribed, user=self.sub_entity_1, unsubscribed_from=test_email_type)
        email = N(Email, send_to=self.super_entity, subentity_type=self.ct, email_type=test_email_type, context={})
        addresses = tasks.get_email_addresses(email)
        expected_addresses = {u'test_sub2@example.com'}
        self.assertEqual(set(addresses), expected_addresses)


class Test_get_html_message(TestCase):
    @patch('__builtin__.open')
    def test_renders_with_context(self, open_mock):
        template_string = 'Hi. This is a {{ value }}.'
        context = {'value': 'test'}
        open_mock.return_value.__enter__.return_value.read.return_value = template_string
        email = N(Email, context=context, html_template_path='some/path')
        rendered = tasks.get_html_message(email)
        expected_rendered = 'Hi. This is a test.'
        self.assertEqual(rendered, expected_rendered)
