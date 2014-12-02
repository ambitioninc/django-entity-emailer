from datetime import datetime, timedelta

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from entity.models import Entity, EntityRelationship, EntityKind

from entity_emailer.models import Email, GroupEmail, IndividualEmail
from entity_emailer.utils import get_admin_source, get_admin_template


def get_all_super_entities_qs():
    """Return a queryset of entities that are superentities.

    Sorted by the number of entities of that type.
    """
    super_entities = EntityRelationship.objects.values_list('super_entity', flat=True).distinct()
    return Entity.objects.filter(pk__in=super_entities).order_by('entity_kind')


def get_all_emailable_entities_qs():
    """Return all the entities that can be emailed.
    """
    entities_with_meta = Entity.objects.filter(entity_meta__isnull=False)
    ids = (e.id for e in entities_with_meta if e.entity_meta.get('email', None) is not None)
    return Entity.objects.filter(pk__in=ids)


class CreateGroupEmailForm(forms.ModelForm):
    subject = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'size': '80'}))
    from_email = forms.EmailField(widget=forms.TextInput(attrs={'size': '80'}))
    to_entity = forms.ModelChoiceField(queryset=get_all_super_entities_qs())
    subentity_kind = forms.ModelChoiceField(queryset=EntityKind.objects.all(), required=False)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'cols': '60'}))
    scheduled_date = forms.DateField(widget=SelectDateWidget(), required=False)
    scheduled_time = forms.TimeField(label="Scheduled time (UTC 24 hr) E.g. 18:25", required=False)

    class Meta:
        model = GroupEmail
        fields = ['subject', 'from_email', 'to_entity', 'subentity_kind', 'body', 'scheduled_date']

    def save(self, *args, **kwargs):
        self.clean()
        scheduled_date = self.cleaned_data['scheduled_date'] or datetime.utcnow().date()
        scheduled_time = self.cleaned_data['scheduled_time'] or datetime.utcnow().time()
        scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
        if not (self.cleaned_data['scheduled_date'] and self.cleaned_data['scheduled_time']):
            scheduled_datetime += timedelta(minutes=5)

        created_email = Email.objects.create(
            source=get_admin_source(),
            subentity_kind=self.cleaned_data['subentity_kind'],
            subject=self.cleaned_data['subject'],
            from_address=self.cleaned_data['from_email'],
            template=get_admin_template(),
            context={'html': self.cleaned_data['body']},
            scheduled=scheduled_datetime
        )
        created_email.recipients.add(self.cleaned_data['to_entity'])
        return created_email

    def save_m2m(self, *args, **kwargs):
        pass


class CreateIndividualEmailForm(forms.ModelForm):
    subject = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'size': '80'}))
    from_email = forms.EmailField(widget=forms.TextInput(attrs={'size': '80'}))
    to_entities = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=FilteredSelectMultiple('Individuals', False)
    )
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'cols': '60'}))
    scheduled_date = forms.DateField(widget=SelectDateWidget(), required=False)
    scheduled_time = forms.TimeField(label="Scheduled time (UTC 24 hr) E.g. 18:25", required=False)

    def __init__(self, *args, **kwargs):
        x = super(CreateIndividualEmailForm, self).__init__(*args, **kwargs)
        self.fields['to_entities'].queryset = get_all_emailable_entities_qs()
        return x

    class Meta:
        model = IndividualEmail
        fields = ['subject', 'from_email', 'to_entities', 'body', 'scheduled_date', 'scheduled_time']

    def save(self, *args, **kwargs):
        self.clean()
        scheduled_date = self.cleaned_data['scheduled_date'] or datetime.utcnow().date()
        scheduled_time = self.cleaned_data['scheduled_time'] or datetime.utcnow().time()
        scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
        if not (self.cleaned_data['scheduled_date'] and self.cleaned_data['scheduled_time']):
            scheduled_datetime += timedelta(minutes=5)

        for entity in self.cleaned_data['to_entities']:
            created_email = Email.objects.create(
                source=get_admin_source(),
                subentity_kind=None,
                subject=self.cleaned_data['subject'],
                from_address=self.cleaned_data['from_email'],
                template=get_admin_template(),
                context={'html': self.cleaned_data['body']},
                scheduled=scheduled_datetime,
            )
            created_email.recipients.add(entity)

        return created_email

    def save_m2m(self, *args, **kwargs):
        pass


class GroupEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'subentity_kind', 'scheduled', 'has_been_sent')
    form = CreateGroupEmailForm

    def get_queryset(self, request):
        qs = super(GroupEmailAdmin, self).get_queryset(request)
        return qs.filter(template=get_admin_template())

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.recipients.first()
        return unicode(send_to_entity)


class IndividualEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'scheduled', 'has_been_sent')
    form = CreateIndividualEmailForm

    def get_queryset(self, request):
        qs = super(IndividualEmailAdmin, self).get_queryset(request)
        return qs.filter(template=get_admin_template())

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.recipients.first()
        return unicode(send_to_entity)


class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'subentity_kind', 'scheduled', 'has_been_sent')

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.recipients.first()
        return unicode(send_to_entity)


admin.site.register(GroupEmail, GroupEmailAdmin)
admin.site.register(IndividualEmail, IndividualEmailAdmin)
admin.site.register(Email, EmailAdmin)
