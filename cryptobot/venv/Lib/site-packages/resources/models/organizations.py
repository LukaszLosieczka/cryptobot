from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Organization(models.Model):
    """
    Defines an organization.
    These can have parent/child relationships.
    """
    name = models.CharField(
        _('name'),
        max_length=100
    )
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        editable=False
    )
    description = models.TextField(
        _('description'),
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        related_name='children',
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
            self.slug = slugify(self.name)

        super(Organization, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'organization'
        verbose_name_plural = 'organizations'
        app_label = 'resources'


class PluginOrganization(CMSPlugin):
    """
    Defines the organization scope of each plugin.
    """
    organization = models.ForeignKey('Organization')

    class Meta:
        app_label = 'resources'
