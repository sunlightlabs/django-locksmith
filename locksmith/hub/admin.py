from django.contrib import admin
from locksmith.hub.models import Key

class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'status', 'email', 'name', 'org_name', 'org_url')
    search_fields = ('key', 'email', 'name', 'org_name')

admin.site.register(Key, KeyAdmin)
