from django.conf.urls import *
from events.views import *

urlpatterns = patterns('events.views',
    url(r'^$', index, name='index'),
    url(r'^(?P<calendar_slug>.*)/(?P<event_slug>.*)/$', event_detail, name='event-detail'),
    url(r'^(?P<calendar_slug>.*)/$', calendar_events, name='calendar-events'),
)
