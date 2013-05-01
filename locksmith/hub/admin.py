from django.contrib import admin
from locksmith.hub.models import Api, Key

class ApiAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'push_enabled')

admin.site.register(Api, ApiAdmin)

class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'status', 'email', 'name', 'org_name', 'org_url')
    search_fields = ('key', 'email', 'name', 'org_name')

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.mark_for_update()

admin.site.register(Key, KeyAdmin)
