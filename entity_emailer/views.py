from django.http import HttpResponse
from django.views.generic import View
from entity_event import context_loader

from entity_emailer.models import Email
from entity_emailer.utils import get_medium


class EmailView(View):
    """
    Provides a basic view for emails that utilizes the html or text templates for rendering.
    Note that it is assumed a url argument of the email view_uid is passed in.
    """
    def get(self, request, *args, **kwargs):
        email = self.get_email()
        medium = get_medium()
        context_loader.load_contexts_and_renderers([email.event], [medium])
        txt, html = email.render(medium)
        return HttpResponse(html if html else txt)

    def get_email(self):
        return Email.objects.select_related('event').get(view_uid=self.args[0])
