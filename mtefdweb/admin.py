from django.contrib import admin

from .models import Funder


class FunderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'perk', 'appearance']
    list_filter = ['perk', 'appearance']
    search_fields = ['name', 'email']

admin.site.register(Funder, FunderAdmin)
