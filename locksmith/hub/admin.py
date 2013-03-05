from django.contrib import admin
from locksmith.hub.models import Api, Key

class ApiAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'push_enabled')

admin.site.register(Api, ApiAdmin)


class KeyAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(KeyAdmin, self).save_model(request, obj, form, change)
        obj.mark_for_update()

admin.site.register(Key, KeyAdmin)
