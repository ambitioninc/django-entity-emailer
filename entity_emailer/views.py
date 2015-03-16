from django.views.generic import TemplateView

from entity_emailer.models import Email


class EmailView(TemplateView):
    """
    Provides a basic view for emails that utilizes the html or text templates for rendering.
    Note that it is assumed a url argument of the email view_uid is passed in.
    """
    def get_email(self):
        return Email.objects.select_related('event').get(view_uid=self.args[0])

    def get_template_names(self):
        email = self.get_email()
        return [email.template.html_template_path, email.template.text_template_path]

    def get_context_data(self):
        return self.get_email().get_context()
