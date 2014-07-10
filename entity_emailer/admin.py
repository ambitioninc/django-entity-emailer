from django.contrib import admin
from entity_emailer.models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'subentity_type', 'scheduled', 'has_been_sent')

    def has_been_sent(self, obj):
        return (obj.sent is not None)

    def to(self, obj):
        send_to_entity = obj.send_to
        return send_to_entity.entity_meta.get('name', unicode(send_to_entity))

admin.site.register(Email, EmailAdmin)
