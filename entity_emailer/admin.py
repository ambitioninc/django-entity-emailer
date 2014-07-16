from datetime import datetime, timedelta

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from entity import Entity, EntityRelationship

from entity_emailer.models import Email
from entity_emailer.utils import get_admin_source, get_admin_template


def get_subentity_content_type_qs():
    """Return a queryset of contenttypes of subentities.

    This queryset filters the contenttypes table to only include the
    contenttypes of subentities mirrored by the Entity framework.
    """
    return ContentType.objects.filter(
        pk__in=EntityRelationship.objects.
        select_related('sub_entity').
        values('sub_entity__entity_type').
        distinct()
    )


def get_all_super_entities_qs():
    """Return a queryset of entities that are superentities.

    Sorted by the number of entities of that type.
    """
    super_entities = EntityRelationship.objects.values_list('super_entity', flat=True).distinct()
    return Entity.objects.filter(pk__in=super_entities).order_by('entity_type')


class CreateEmailForm(forms.ModelForm):
    subject = forms.CharField(max_length=128)
    from_email = forms.EmailField()
    to_entity = forms.ModelChoiceField(queryset=get_all_super_entities_qs())
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
            template=get_admin_template(),
            context={'html': self.cleaned_data['body']},
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
        return unicode(send_to_entity)


admin.site.register(Email, EmailAdmin)
