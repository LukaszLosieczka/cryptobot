from django.db import models
from cms.models import CMSPlugin
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from resources.models import Organization
from resources.models import Person


class Calendar(models.Model):
    """
    Defines a calendar for which events will be tracked.
    """
    name = models.CharField(_('Calendar Name'), max_length=64)
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        editable=False
    )

    """
    Overide the save method to auto-slug.
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            # Set slug only if new to keep from breaking links.
            self.slug = slugify(self.name)

        super(Calendar, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'calendar'
        verbose_name_plural = 'calendars'
        app_label = 'events'


class Event(models.Model):
    """
    Defines events on a single calendar.
    """
    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        editable=False
    )
    start = models.DateTimeField(_('Starts'), null=True, blank=True)
    end = models.DateTimeField(_('Ends'), null=True, blank=True)
    audience = models.TextField(
        _('Audience'),
        help_text="Who is expected or allowed to attend this event?",
        null=True,
        blank=True
    )
    description = models.TextField(
        _('Description'),
        help_text="Describe the event. For instance: topics to be covered, and what to bring.",
        null=True,
        blank=True
    )
    max_size = models.IntegerField(
        _('Maximum Event Size'),
        max_length=4,
        null=True,
        blank=True
    )
    calendar = models.ForeignKey('Calendar')
    location = models.ForeignKey(
        Organization,
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        Person,
        null=True,
        blank=True
    )

    """
    Overide the save method to auto-slug.
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            # Set slug only if new to keep from breaking links.
            self.slug = slugify(self.name)

        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'event'
        verbose_name_plural = 'events'
        app_label = 'events'


class CalendarEventsPlugin(CMSPlugin):
    """
    Plugin to show upcoming events from one calendar.
    """
    calendar = models.ForeignKey('Calendar')
    number_to_show = models.IntegerField(
        max_length=4,
    )


class AllEventsPlugin(CMSPlugin):
    """
    Plugin to show upcoming events from all calendars.
    """
    number_to_show = models.IntegerField(
        max_length=4,
    )

