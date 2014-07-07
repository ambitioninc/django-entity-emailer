from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django_dynamic_fixture import G, N
from entity.models import Entity, EntityRelationship
from entity_subscription.models import Medium, Source, Subscription, Unsubscribe
from freezegun import freeze_time
from mock import patch

from entity_emailer import tasks
from entity_emailer.models import Email, EmailTemplate


@freeze_time('2014-01-05')
class SendUnsentScheduledEmailsTest(TestCase):
    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.render_to_string')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    def test_sends_all_scheduled_emails(self, address_mock, loader_mock):
        loader_mock.side_effect = ['<p>This is a test html email.</p>',
                                   'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        template = G(EmailTemplate, text_template='Hi')
        G(Email, template=template, context={}, scheduled=datetime.min)
        G(Email, template=template, context={}, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.render_to_string')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    def test_sends_email_with_specified_from_address(self, address_mock, loader_mock):
        loader_mock.side_effect = ['<p>This is a test html email.</p>',
                                   'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        template = G(EmailTemplate, text_template='Hi')
        from_address = 'test@example.com'
        G(Email, template=template, context={}, from_address=from_address, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(mail.outbox[0].from_email, from_address)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.render_to_string')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    def test_sends_no_future_emails(self, address_mock, loader_mock):
        loader_mock.side_effect = ['<p>This is a test html email.</p>',
                                   'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        template = G(EmailTemplate, text_template='Hi')
        G(Email, template=template, context={}, scheduled=datetime(2014, 01, 06))
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.render_to_string')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    def test_sends_no_sent_emails(self, address_mock, loader_mock):
        loader_mock.side_effect = ['<p>This is a test html email.</p>',
                                   'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        template = G(EmailTemplate, text_template='Hi')
        G(Email, template=template, context={}, scheduled=datetime.min, sent=datetime.utcnow())
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.render_to_string')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    def test_updates_times(self, address_mock, loader_mock):
        loader_mock.side_effect = ['<p>This is a test html email.</p>',
                                   'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        template = G(EmailTemplate, text_template='Hi')
        G(Email, template=template, context={}, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        sent_email = Email.objects.filter(sent__isnull=False)
        self.assertEqual(sent_email.count(), 1)


class CreateEmailObjectTest(TestCase):
    def test_no_html(self):
        email = tasks.create_email_message(
            ['to@example.com'], 'from@example.com', 'Subject', 'Email Body.', ''
        )
        email.send()
        self.assertEqual(mail.outbox[0].attachments, [])

    def test_html(self):
        email = tasks.create_email_message(
            ['to@example.com'], 'from@example.com', 'Subject', 'Email Body.', '<html>A</html>'
        )
        email.send()
        expected_alternatives = [('<html>A</html>', 'text/html')]
        self.assertEqual(mail.outbox[0].alternatives, expected_alternatives)


class GetFromEmailAddressTest(TestCase):
    def test_default_from_email(self):
        # settings.DEFAULT_FROM_EMAIL is already set to test@example.com
        from_email = tasks.get_from_email_address()
        expected = 'test@example.com'
        self.assertEqual(from_email, expected)

    @override_settings(ENTITY_EMAILER_FROM_EMAIL='test_entity@example.com')
    def test_entity_emailer_from_email(self):
        from_email = tasks.get_from_email_address()
        expected = 'test_entity@example.com'
        self.assertEqual(from_email, expected)


class GetEmailAddressesTest(TestCase):
    def setUp(self):
        self.ct = G(ContentType)
        self.ct2 = G(ContentType)
        self.super_entity = G(Entity, entity_meta={'email': 'test_super@example.com'}, entity_type=self.ct)
        self.sub_entity_1 = G(Entity, entity_meta={'email': 'test_sub1@example.com'}, entity_type=self.ct)
        self.sub_entity_2 = G(Entity, entity_meta={'email': 'test_sub2@example.com'}, entity_type=self.ct)
        self.sub_entity_3 = G(Entity, entity_meta={'email': 'test_sub3@example.com'}, entity_type=self.ct2)
        G(EntityRelationship, sub_entity=self.sub_entity_1, super_entity=self.super_entity)
        G(EntityRelationship, sub_entity=self.sub_entity_2, super_entity=self.super_entity)
        G(EntityRelationship, sub_entity=self.sub_entity_3, super_entity=self.super_entity)
        self.template = G(EmailTemplate, text_template='Hi!')
        self.medium = G(Medium, name='email')
        self.source = G(Source, name='test_email')

    def test_returns_sub_entities_emails(self):
        G(Subscription, entity=self.super_entity, subentity_type=self.ct, medium=self.medium, source=self.source)
        email = N(
            Email, source=self.source, send_to=self.super_entity,
            subentity_type=self.ct, template=self.template, context={}
        )
        addresses = tasks.get_subscribed_email_addresses(email)
        expected_addresses = {u'test_sub1@example.com', u'test_sub2@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_filters_other_entity_types(self):
        G(Subscription, entity=self.super_entity, subentity_type=self.ct2, medium=self.medium, source=self.source)
        email = N(
            Email, source=self.source, send_to=self.super_entity,
            subentity_type=self.ct2, template=self.template, context={}
        )
        addresses = tasks.get_subscribed_email_addresses(email)
        expected_addresses = {u'test_sub3@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_returns_own_email(self):
        G(Subscription, entity=self.super_entity, subentity_type=None, medium=self.medium, source=self.source)
        email = N(
            Email, source=self.source, send_to=self.super_entity,
            subentity_type=None, template=self.template, context={}
        )
        addresses = tasks.get_subscribed_email_addresses(email)
        expected_addresses = {u'test_super@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_unsubscription_works(self):
        G(Subscription, entity=self.super_entity, subentity_type=self.ct, medium=self.medium, source=self.source)
        G(Unsubscribe, entity=self.sub_entity_1, source=self.source, medium=self.medium)
        email = N(
            Email, send_to=self.super_entity, subentity_type=self.ct,
            source=self.source, template=self.template, context={}
        )
        addresses = tasks.get_subscribed_email_addresses(email)
        expected_addresses = {u'test_sub2@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_email_settings(self):
        custom_medium_name = 'test_medium'
        other_medium = G(Medium, name=custom_medium_name)
        G(Subscription, entity=self.super_entity, subentity_type=self.ct, medium=other_medium, source=self.source)
        email = N(
            Email, source=self.source, send_to=self.super_entity,
            subentity_type=self.ct, template=self.template, context={}
        )
        expected_addresses = {u'test_sub1@example.com', u'test_sub2@example.com'}
        with self.settings(ENTITY_EMAILER_MEDIUM_NAME=custom_medium_name):
            addresses = tasks.get_subscribed_email_addresses(email)
        self.assertEqual(set(addresses), expected_addresses)


class RenderTemplatesTest(TestCase):
    @patch('__builtin__.open')
    def test_text_path(self, open_mock):
        open_mock.return_value.__enter__.return_value.read.return_value = 'Hi {{ name }}'
        template = G(EmailTemplate, text_template_path='NotNothing')
        email = N(Email, template=template, context={'name': 'Mr. T'})
        rendered_text, rendered_html = tasks.render_templates(email)
        self.assertEqual(rendered_text, 'Hi Mr. T')
        self.assertEqual(rendered_html, '')

    def test_text_textfield(self):
        template = G(EmailTemplate, text_template='Hi {{ name }}')
        email = N(Email, template=template, context={'name': 'Mr. T'})
        rendered_text, rendered_html = tasks.render_templates(email)
        self.assertEqual(rendered_text, 'Hi Mr. T')
        self.assertEqual(rendered_html, '')

    @patch('__builtin__.open')
    def test_html_path(self, open_mock):
        temp = '<html>Hi {{ name }}</html>'
        open_mock.return_value.__enter__.return_value.read.return_value = temp
        template = G(EmailTemplate, html_template_path='NotNothing')
        email = N(Email, template=template, context={'name': 'Mr. T'})
        rendered_text, rendered_html = tasks.render_templates(email)
        self.assertEqual(rendered_text, '')
        self.assertEqual(rendered_html, '<html>Hi Mr. T</html>')

    def test_test_textfield(self):
        temp = '<html>Hi {{ name }}</html>'
        template = G(EmailTemplate, html_template=temp)
        email = N(Email, template=template, context={'name': 'Mr. T'})
        rendered_text, rendered_html = tasks.render_templates(email)
        self.assertEqual(rendered_text, '')
        self.assertEqual(rendered_html, '<html>Hi Mr. T</html>')
