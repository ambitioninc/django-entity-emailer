from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import G
from entity.models import Entity
from entity_event.models import Event
from freezegun import freeze_time

from entity_emailer.models import Email


class EmailManagerCreateEmailTest(TestCase):
    @freeze_time('2013-2-3')
    def test_w_recipients_scheduled_time(self):
        e1 = G(Entity)
        e2 = G(Entity)
        event = G(Event, context={'hi': 'hi'})
        e = Email.objects.create_email(
            scheduled=datetime(2013, 4, 5), recipients=[e1, e2],
            subject='hi', from_address='hi@hi.com', event=event, uid='hi')
        self.assertEqual(e.scheduled, datetime(2013, 4, 5))
        self.assertEqual(set(e.recipients.all()), set([e1, e2]))
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.event.context, {'hi': 'hi'})
        self.assertEqual(e.uid, 'hi')

    @freeze_time('2013-2-3')
    def test_w_recipients_no_scheduled_time(self):
        e1 = G(Entity)
        e2 = G(Entity)
        event = G(Event, context={'hi': 'hi'})
        e = Email.objects.create_email(
            recipients=[e1, e2], subject='hi', from_address='hi@hi.com',
            event=event, uid='hi')
        self.assertEqual(e.scheduled, datetime(2013, 2, 3))
        self.assertEqual(set(e.recipients.all()), set([e1, e2]))
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.event.context, {'hi': 'hi'})
        self.assertEqual(e.uid, 'hi')

    @freeze_time('2013-2-3')
    def test_w_recipients_no_scheduled_time_no_recipients_no_uid(self):
        event = G(Event, context={'hi': 'hi'})
        e = Email.objects.create_email(
            subject='hi', from_address='hi@hi.com', event=event)
        self.assertEqual(e.scheduled, datetime(2013, 2, 3))
        self.assertEqual(list(e.recipients.all()), [])
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.event.context, {'hi': 'hi'})
        self.assertIsNone(e.uid)
