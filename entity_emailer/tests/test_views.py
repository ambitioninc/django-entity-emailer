from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from entity.models import Entity
from entity_event.models import Medium, RenderingStyle, ContextRenderer, Source, Event
import six

from entity_emailer.tests.utils import g_email


class EmailViewTest(TestCase):
    def setUp(self):
        self.rendering_style = G(RenderingStyle, name='email')
        G(Medium, name='email', rendering_style=self.rendering_style)
        self.source = G(Source)

    def test_html_path(self):
        G(
            ContextRenderer, source=self.source, html_template_path='hi_template.html',
            rendering_style=self.rendering_style, context_hints={
                'entity': {
                    'app_name': 'entity',
                    'model_name': 'Entity',
                }
            })
        person = G(Entity, display_name='Swansonbot')
        event = G(Event, context={'entity': person.id}, source=self.source)
        email = g_email(event=event)

        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        content = response.content
        if six.PY3:  # pragma: no cover
            content = content.decode('utf8')

        self.assertEqual(content, '<html>Hi Swansonbot</html>')

    def test_text_path(self):
        G(
            ContextRenderer, source=self.source, html_template_path='hi_template.txt',
            rendering_style=self.rendering_style, context_hints={
                'entity': {
                    'app_name': 'entity',
                    'model_name': 'Entity',
                }
            })
        person = G(Entity, display_name='Swansonbot')
        event = G(Event, context={'entity': person.id}, source=self.source)
        email = g_email(event=event)
        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        content = response.content
        if six.PY3:  # pragma: no cover
            content = content.decode('utf8')
        self.assertEqual(content, 'Hi Swansonbot')

    def test_text_and_html_path(self):
        G(
            ContextRenderer, source=self.source,
            html_template_path='hi_template.html', text_template_path='hi_template.txt',
            rendering_style=self.rendering_style, context_hints={
                'entity': {
                    'app_name': 'entity',
                    'model_name': 'Entity',
                }
            })

        person = G(Entity, display_name='Swansonbot')
        event = G(Event, context={'entity': person.id}, source=self.source)
        email = g_email(context={'entity': person.id})
        email = g_email(event=event)

        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        content = response.content
        if six.PY3:  # pragma: no cover
            content = content.decode('utf8')

        self.assertEqual(content, '<html>Hi Swansonbot</html>')
