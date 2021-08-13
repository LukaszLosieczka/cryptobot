from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from resources.models.organizations import Organization


class Person(models.Model):
    """
    Defines a person.
    These can have parent/child relationships.
    """
    name_first = models.CharField(
        _('first name'),
        max_length=50
    )
    name_last = models.CharField(
        _('last name'),
        max_length=50
    )
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        editable=False
    )
    title = models.CharField(
        _('title'),
        max_length=100,
        null=True,
        blank=True
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        blank=True,
        null=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    """
    Overide the save method to auto-slug.
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            # Set slug only if new to keep from breaking links.
            self.slug = slugify("%s %s" % (self.name_first, self.name_last))

        super(Person, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s %s" % (self.name_first, self.name_last)

    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'people'
        app_label = 'resources'
