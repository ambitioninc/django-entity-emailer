from django.contrib import admin
from entity_emailer.models import Email


class EmailAdmin(admin.ModelAdmin):
    pass


admin.site.register(Email, EmailAdmin)
