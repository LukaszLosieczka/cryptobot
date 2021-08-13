from django.db import models
from django.utils.translation import ugettext_lazy as _
from localflavor.us.models import USStateField
from localflavor.us.models import PhoneNumberField
from localflavor.us.us_states import USPS_CHOICES
from resources.models.organizations import Organization
from resources.models.people import Person


class Address(models.Model):
    """
    Address of type.
    Attached to people and organizations.
    """
    address1 = models.CharField(
        _('address 1'),
        max_length=100,
        null=True,
        blank=True
    )
    address2 = models.CharField(
        _('address 2'),
        max_length=100,
        null=True,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=64,
        null=True,
        blank=True)
    state = USStateField(
        _('state'),
        choices=USPS_CHOICES, null=True,
        blank=True)
    zipcode = models.CharField(
        _('zip code'),
        max_length=10,
        null=True,
        blank=True)
    TYPES_CHOICES = (
        ('Work', _('Work')),
        ('Home', _('Home')),
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPES_CHOICES,
        default=TYPES_CHOICES[0][0]
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        null=True,
        blank=True
    )
    person = models.ForeignKey(
        'Person',
        verbose_name='person',
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return u"%s | %s" % (self.address1, self.type)

    class Meta:
        verbose_name = 'address'
        verbose_name_plural = 'addresses'
        app_label = 'resources'


class Email(models.Model):
    """
    Addresses associated with organizations or people.
    """
    address = models.EmailField(
        _('address'),
        max_length=200,
        null=False,
        blank=False
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        null=True,
        blank=True
    )
    person = models.ForeignKey(
        'Person',
        verbose_name='person',
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return self.address

    class Meta:
        verbose_name = 'email address'
        verbose_name_plural = 'email addresses'
        app_label = 'resources'


class Phone(models.Model):
    """
    Phone numbers of type.
    Attached to people and organizations.
    """
    number = PhoneNumberField(
        _('number'),
        null=False,
        blank=False
    )
    TYPES_CHOICES = (
        ('Mobile', _('Mobile')),
        ('Home', _('Home')),
        ('Work', _('Work')),
        ('Fax', _('Fax')),
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPES_CHOICES,
        default=TYPES_CHOICES[0][0]
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        null=True,
        blank=True
    )
    person = models.ForeignKey(
        'Person',
        verbose_name='person',
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return u"%s | %s" % (self.number, self.type)

    class Meta:
        verbose_name = 'phone number'
        verbose_name_plural = 'phone numbers'
        app_label = 'resources'


class Website(models.Model):
    """
    Website URL's
    """
    url = models.URLField(
        _('url'),
        null=False,
        blank=False
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        null=True,
        blank=True
    )
    person = models.ForeignKey(
        'Person',
        verbose_name='person',
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return u"%s" % (self.url)

    class Meta:
        verbose_name = 'website'
        verbose_name_plural = 'websites'
        app_label = 'resources'


class Profile(models.Model):
    """
    Profile URL's
    """
    url = models.URLField(
        _('url'),
        null=False,
        blank=False
    )
    TYPES_CHOICES = (
        ('GooglePlus', _('Google+')),
        ('Facebook', _('Facebook')),
        ('Twitter', _('Twitter')),
        ('Linkedin', _('Linkedin')),
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPES_CHOICES,
        default=TYPES_CHOICES[0][0]
    )
    organization = models.ForeignKey(
        'Organization',
        verbose_name='organization',
        null=True,
        blank=True
    )
    person = models.ForeignKey(
        'Person',
        verbose_name='person',
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return u"%s | %s" % (self.url, self.type)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
        app_label = 'resources'
