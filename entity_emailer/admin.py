from datetime import datetime, timedelta

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from entity import Entity, EntityRelationship

from entity_emailer.models import Email, EmailTemplate
from entity_emailer.utils import get_admin_source


def get_subentity_content_type_qs():
    """Return a queryset of contenttypes of subentities.

    This queryset filters the contenttypes table to only include the
    contenttypes of subentities mirrored by the Entity framework.
    """
    return ContentType.objects.filter(
        pk__in=EntityRelationship.objects.
        select_related('sub_entity').
        distinct('sub_entity__entity_type').
        values('sub_entity__entity_type')
    )


class CreateEmailForm(forms.ModelForm):
    subject = forms.CharField(max_length=128)
    from_email = forms.EmailField()
    to_entity = forms.ModelChoiceField(queryset=Entity.objects.all())
    subentity_type = forms.ModelChoiceField(queryset=get_subentity_content_type_qs(), required=False)
    body = forms.CharField(widget=forms.Textarea)
    scheduled = forms.DateTimeField(required=False)

    class Meta:
        model = Email
        fields = ['subject', 'from_email', 'to_entity', 'subentity_type', 'body', 'scheduled']

    def save(self, *args, **kwargs):
        self.clean()
        scheduled = self.cleaned_data['scheduled'] or (datetime.utcnow() + timedelta(minutes=5))
        created_email = Email(
            source=get_admin_source(),
            send_to=self.cleaned_data['to_entity'],
            subentity_type=self.cleaned_data['subentity_type'],
            subject=self.cleaned_data['subject'],
            from_address=self.cleaned_data['from_email'],
            template=EmailTemplate.objects.get(template_name='test_html_safe'),
            context=self.cleaned_data['body'],
            scheduled=scheduled
        )
        created_email.save()
        return created_email

    def save_m2m(self, *args, **kwargs):
        pass


class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'subentity_type', 'scheduled', 'has_been_sent')
    form = CreateEmailForm

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.send_to
        try:
            return send_to_entity.entity_meta.get('name', unicode(send_to_entity))
        except AttributeError:
            return 'Entity Object'


admin.site.register(Email, EmailAdmin)
