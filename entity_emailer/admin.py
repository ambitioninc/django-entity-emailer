from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from entity import Entity

from entity_emailer.models import Email


class CreateEmailForm(forms.ModelForm):
    subject = forms.CharField(max_length=128)
    from_email = forms.EmailField()
    to_entity = forms.ModelChoiceField(queryset=Entity.objects.all())
    subentity_type = forms.ModelChoiceField(queryset=ContentType.objects.all())
    body = forms.CharField(widget=forms.Textarea)
    scheduled = forms.DateTimeField()

    class Meta:
        model = Email
        fields = ['subject', 'from_email', 'to_entity', 'subentity_type', 'body', 'scheduled']


class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'subentity_type', 'scheduled', 'has_been_sent')
    form = CreateEmailForm

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.send_to
        return send_to_entity.entity_meta.get('name', unicode(send_to_entity))


admin.site.register(Email, EmailAdmin)
