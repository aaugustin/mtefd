from django.contrib import admin
from django.utils.html import format_html

from .models import Funder, Update


class FunderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'perk', 'appearance', 'info_url']
    list_filter = ['perk', 'appearance']
    search_fields = ['name', 'email']

    def info_url(self, obj):
        return format_html('<a href="{}">{}</a>',
                           obj.get_absolute_url(), obj.token)


admin.site.register(Funder, FunderAdmin)


class UpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ['title', 'date']
    search_fields = ['title', 'body']


admin.site.register(Update, UpdateAdmin)
