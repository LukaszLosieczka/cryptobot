from django.contrib import admin
from events.models import Calendar
from events.models import Event


class CalendarAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Calendar', {
            'fields': ['name']
        }),
    ]
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ['name']


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Event', {
            'fields': [
                'calendar',
                'name',
                'location',
                ('start', 'end',),
                'max_size',
                'audience',
                'description',
                'contact'
            ]
        }),
    ]
    list_display = ('name', 'calendar', 'location', 'start', 'end')
    list_display_links = ('name',)
    ordering = ('start',)
    list_filter = ('calendar__name', 'location', 'contact')
    search_fields = ['calendar__name', 'contact']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)
