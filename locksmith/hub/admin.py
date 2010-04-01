from django.contrib import admin
from locksmith.hub.models import Api

class ApiAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

admin.site.register(Api, ApiAdmin)
