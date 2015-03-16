from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G, F
from entity.models import Entity

from entity_emailer.tests.utils import g_email


def render_template_context_loader(context):
    return {
        'entity': Entity.objects.get(id=context['entity']).display_name
    }


class EmailViewTest(TestCase):
    def test_html_path_with_context_loader(self):
        person = G(Entity, display_name='Swansonbot')
        email = g_email(
            template=F(html_template_path='hi_template.html'), context={'entity': person.id},
            source=F(context_loader='entity_emailer.tests.test_views.render_template_context_loader'))

        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        self.assertEqual(response.content, '<html>Hi Swansonbot</html>')

    def test_text_path_with_context_loader(self):
        person = G(Entity, display_name='Swansonbot')
        email = g_email(
            template=F(text_template_path='hi_template.txt'), context={'entity': person.id},
            source=F(context_loader='entity_emailer.tests.test_views.render_template_context_loader'))
        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        self.assertEqual(response.content, 'Hi Swansonbot')

    def test_text_and_html_path_with_context_loader(self):
        template = G(
            EmailTemplate, html_template_path='hi_template.html', text_template_path='hi_template.txt',
            context_loader='entity_emailer.tests.test_views.render_template_context_loader')
        person = G(Entity, display_name='Swansonbot')
        email = g_email(template=template, context={'entity': person.id})
        email = g_email(
            template=F(html_template_path='hi_template.html', text_template_path='hi_template.txt'),
            context={'entity': person.id},
            source=F(context_loader='entity_emailer.tests.test_views.render_template_context_loader'))

        url = reverse('entity_emailer.email', args=[email.view_uid])
        response = self.client.get(url)
        self.assertEqual(response.content, '<html>Hi Swansonbot</html>')
