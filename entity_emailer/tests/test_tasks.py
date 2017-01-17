from datetime import datetime

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from django.test.utils import override_settings
from django_dynamic_fixture import G
from entity.models import Entity, EntityRelationship, EntityKind
from entity_event.models import (
    Medium, Source, Subscription, Unsubscription, Event, EventActor
)
from freezegun import freeze_time
from mock import patch

from entity_emailer import tasks
from entity_emailer.models import Email
from entity_emailer.tests.utils import g_email


class ExtractEmailSubjectFromHtmlContentTest(SimpleTestCase):
    def test_blank(self):
        subject = tasks.extract_email_subject_from_html_content('')
        self.assertEquals(subject, '')

    def test_with_title_block(self):
        subject = tasks.extract_email_subject_from_html_content('<html><head><title> Hello! </title></head></html>')
        self.assertEquals(subject, 'Hello!')

    def test_wo_title_block_under_40_chars_content(self):
        subject = tasks.extract_email_subject_from_html_content(' Small content ')
        self.assertEquals(subject, 'Small content')

    def test_wo_title_block_under_40_chars_multiline_content(self):
        subject = tasks.extract_email_subject_from_html_content((
            ' Small content \n'
            'that spans multiple lines'
        ))
        self.assertEquals(subject, 'Small content')

    def test_wo_title_block_gt_40_chars_content(self):
        subject = tasks.extract_email_subject_from_html_content((
            ' This is reallly long content that is greater than 40 chars on the first line. It should have ...'
        ))
        self.assertEquals(subject, 'This is reallly long content that is gre...')


class ConvertEventsToEmailsTest(TestCase):
    def setUp(self):
        call_command('add_email_medium')
        self.email_medium = Medium.objects.get(name='email')

    @patch('entity_emailer.tasks.convert_events_to_emails', spec_set=True)
    def test_task(self, mock_convert_events_to_emails):
        tasks.ConvertEventsToEmails().run()
        mock_convert_events_to_emails.assert_called_once_with()

    def test_no_events(self):
        tasks.convert_events_to_emails()
        self.assertFalse(Email.objects.exists())

    def test_no_subscriptions(self):
        G(Event, context={})
        tasks.convert_events_to_emails()
        self.assertFalse(Email.objects.exists())

    @freeze_time('2013-1-2')
    def test_basic_only_following_false_subscription(self):
        source = G(Source)
        e = G(Entity)
        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=False, sub_entity_kind=None)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        self.assertEquals(list(email.recipients.all()), [e])
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_basic_only_following_false_subscription_marked_seen(self):
        source = G(Source)
        e = G(Entity)
        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=False, sub_entity_kind=None)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()
        tasks.convert_events_to_emails()

        email = Email.objects.get()
        self.assertEquals(list(email.recipients.all()), [e])
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_basic_only_following_true_subscription(self):
        source = G(Source)
        e = G(Entity)
        se = G(Entity)
        G(EntityRelationship, sub_entity=e, super_entity=se)
        other_e = G(Entity)

        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=True)
        G(Subscription, entity=other_e, source=source, medium=self.email_medium, only_following=True)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=se)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        # Since the other_e entity does not follow the se entity, only the e entity receives an email
        self.assertEquals(set(email.recipients.all()), set([e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_super_entity_only_following_false_subscription(self):
        source = G(Source)
        e = G(Entity)
        se = G(Entity)
        G(EntityRelationship, sub_entity=e, super_entity=se)
        other_e = G(Entity)

        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=False)
        G(Subscription, entity=other_e, source=source, medium=self.email_medium, only_following=False)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=se)
        G(EventActor, event=event, entity=other_e)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        self.assertEquals(set(email.recipients.all()), set([e, other_e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_basic_only_following_true_group_subscription(self):
        source = G(Source)
        ek = G(EntityKind)
        e = G(Entity, entity_kind=ek)
        se = G(Entity)
        G(EntityRelationship, sub_entity=e, super_entity=se)
        other_e = G(Entity, entity_kind=ek)
        G(EntityRelationship, sub_entity=other_e, super_entity=se)

        G(Subscription, entity=se, sub_entity_kind=ek, source=source, medium=self.email_medium, only_following=True)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=se)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        # Both entities are subscribed with a group subscription and are following the super entity of the event
        self.assertEquals(set(email.recipients.all()), set([e, other_e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_basic_only_following_false_group_subscription(self):
        source = G(Source)
        ek = G(EntityKind)
        e = G(Entity, entity_kind=ek)
        se = G(Entity)
        G(EntityRelationship, sub_entity=e, super_entity=se)
        other_e = G(Entity, entity_kind=ek)
        G(EntityRelationship, sub_entity=other_e, super_entity=se)

        G(Subscription, entity=se, sub_entity_kind=ek, source=source, medium=self.email_medium, only_following=False)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        # Both entities are subscribed with a group subscription and are following the super entity of the event
        self.assertEquals(set(email.recipients.all()), set([e, other_e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_basic_only_following_false_group_subscription_with_unsubscribed(self):
        source = G(Source)
        ek = G(EntityKind)
        e = G(Entity, entity_kind=ek)
        se = G(Entity)
        G(EntityRelationship, sub_entity=e, super_entity=se)
        other_e = G(Entity, entity_kind=ek)
        G(EntityRelationship, sub_entity=other_e, super_entity=se)

        G(Subscription, entity=se, sub_entity_kind=ek, source=source, medium=self.email_medium, only_following=False)
        G(Unsubscription, entity=e, source=source, medium=self.email_medium)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        self.assertEquals(set(email.recipients.all()), set([other_e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_multiple_events_only_following_false(self):
        source = G(Source)
        e = G(Entity)
        other_e = G(Entity)

        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=False)
        G(Subscription, entity=other_e, source=source, medium=self.email_medium, only_following=False)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        G(Event, source=source, context=email_context)
        G(Event, source=source, context=email_context)

        tasks.convert_events_to_emails()

        self.assertEquals(Email.objects.count(), 2)
        for email in Email.objects.all():
            self.assertEquals(set(email.recipients.all()), set([e, other_e]))
            self.assertEquals(email.event.context, email_context)
            self.assertEquals(email.subject, '')
            self.assertEquals(email.scheduled, datetime(2013, 1, 2))

    @freeze_time('2013-1-2')
    def test_multiple_events_only_following_true(self):
        source = G(Source)
        e = G(Entity)
        other_e = G(Entity)

        G(Subscription, entity=e, source=source, medium=self.email_medium, only_following=True)
        G(Subscription, entity=other_e, source=source, medium=self.email_medium, only_following=True)
        email_context = {
            'entity_emailer_template': 'template',
            'entity_emailer_subject': 'hi',
        }
        G(Event, source=source, context=email_context)
        event = G(Event, source=source, context=email_context)
        G(EventActor, event=event, entity=e)

        tasks.convert_events_to_emails()

        email = Email.objects.get()
        self.assertEquals(set(email.recipients.all()), set([e]))
        self.assertEquals(email.event.context, email_context)
        self.assertEquals(email.subject, '')
        self.assertEquals(email.scheduled, datetime(2013, 1, 2))


@freeze_time('2014-01-05')
class SendUnsentScheduledEmailsTest(TestCase):
    def setUp(self):
        G(Medium, name='email')

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_sends_all_scheduled_emails_no_email_addresses(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = []
        g_email(context={}, scheduled=datetime.min)
        g_email(context={}, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_sends_all_scheduled_emails(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        g_email(context={}, scheduled=datetime.min)
        g_email(context={}, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_sends_email_with_specified_from_address(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        from_address = 'test@example.com'
        g_email(context={}, from_address=from_address, scheduled=datetime.min)
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(mail.outbox[0].from_email, from_address)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_sends_no_future_emails(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        g_email(context={}, scheduled=datetime(2014, 1, 6))
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_sends_no_sent_emails(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        g_email(context={}, scheduled=datetime.min, sent=datetime.utcnow())
        tasks.SendUnsentScheduledEmails().delay()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, BROKER_BACKEND='memory')
    @patch('entity_emailer.tasks.get_subscribed_email_addresses')
    @patch.object(Event, 'render', spec_set=True)
    def test_updates_times(self, render_mock, address_mock):
        render_mock.return_value = ['<p>This is a test html email.</p>', 'This is a test text email.']
        address_mock.return_value = ['test1@example.com', 'test2@example.com']
        g_email(context={}, scheduled=datetime.min)
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


class GetSubscribedEmailAddressesTest(TestCase):
    def test_get_emails_default_settings(self):
        e1 = G(Entity, entity_meta={'email': 'hello1@hello.com'})
        e2 = G(Entity, entity_meta={'email': 'hello2@hello.com'})
        e3 = G(Entity, entity_meta={'email': ''})
        e4 = G(Entity, entity_meta={})
        email = g_email(recipients=[e1, e2, e3, e4], context={})

        addresses = tasks.get_subscribed_email_addresses(email)
        self.assertEqual(set(addresses), set(['hello1@hello.com', 'hello2@hello.com']))

    @override_settings(ENTITY_EMAILER_EMAIL_KEY='email_address')
    @override_settings(ENTITY_EMAILER_EXCLUDE_KEY='last_invite_time')
    def test_get_emails_override_email_key(self):
        e1 = G(Entity, entity_meta={'email_address': 'hello1@hello.com', 'last_invite_time': 1000})
        e2 = G(Entity, entity_meta={'email_address': 'hello2@hello.com', 'last_invite_time': None})
        email = g_email(recipients=[e1, e2], context={})

        addresses = tasks.get_subscribed_email_addresses(email)
        self.assertEqual(set(addresses), set(['hello1@hello.com']))

    @override_settings(ENTITY_EMAILER_EMAIL_KEY='email_address')
    def test_get_emails_override_email_key_exclude_key(self):
        e1 = G(Entity, entity_meta={'email_address': 'hello1@hello.com'})
        e2 = G(Entity, entity_meta={'email_address': 'hello2@hello.com'})
        email = g_email(recipients=[e1, e2], context={})

        addresses = tasks.get_subscribed_email_addresses(email)
        self.assertEqual(set(addresses), set(['hello1@hello.com', 'hello2@hello.com']))


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
    def test_returns_own_email(self):
        entity_1 = G(Entity, entity_meta={'email': 'test_1@example.com'})
        entity_2 = G(Entity, entity_meta={'email': 'test_2@example.com'})
        email = g_email(recipients=[entity_1, entity_2], context={})
        addresses = tasks.get_subscribed_email_addresses(email)
        expected_addresses = {u'test_1@example.com', u'test_2@example.com'}
        self.assertEqual(set(addresses), expected_addresses)

    def test_no_recipients(self):
        email = g_email(recipients=[], context={})
        addresses = tasks.get_subscribed_email_addresses(email)
        self.assertEqual(addresses, [])
