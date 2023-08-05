from django.contrib import admin

from ..models import ConteudoCustom


@admin.register(ConteudoCustom)
class ConteudoCustomAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'local',
    ]

    search_fields = [
        'id',
        'local',
    ]

    list_filter = [
        'local',
    ]
