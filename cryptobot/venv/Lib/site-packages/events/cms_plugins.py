from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
import datetime
from django.utils.translation import ugettext as _
from events.models import CalendarEventsPlugin as CalendarEventsPluginModel
from events.models import AllEventsPlugin as AllEventsPluginModel
from events.models import Event


class CalendarEventsPlugin(CMSPluginBase):
    model = CalendarEventsPluginModel
    name = _("Events (from one calendar)")
    render_template = "events/plugin.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        events = Event.objects.filter(calendar__id=instance.calendar.id).filter(end__gte=datetime.date.today()).order_by('start')[:instance.number_to_show]
        context.update({
            'instance': instance,
            'events': events,
            'placeholder': placeholder,
        })
        return context


class AllEventsPlugin(CMSPluginBase):
    model = AllEventsPluginModel
    name = _("Events (all calendars)")
    render_template = "events/plugin.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        events = Event.objects.filter(end__gte=datetime.date.today()).order_by('start')[:instance.number_to_show]
        context.update({
            'instance': instance,
            'events': events,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CalendarEventsPlugin)
plugin_pool.register_plugin(AllEventsPlugin)

