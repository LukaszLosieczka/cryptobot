from resources.models import Person
from resources.models import Address
from resources.models import Email
from resources.models import Phone
from resources.models import Website
from resources.models import Profile
from django.contrib import admin


class AddressAdminInline(admin.StackedInline):
    model = Address
    exclude = ['organization']
    extra = 0


class EmailAdminInline(admin.StackedInline):
    model = Email
    exclude = ['organization']
    extra = 0


class PhoneAdminInline(admin.StackedInline):
    model = Phone
    exclude = ['organization']
    extra = 0


class WebsiteAdminInline(admin.StackedInline):
    model = Website
    exclude = ['organization']
    extra = 0


class ProfileAdminInline(admin.StackedInline):
    model = Profile
    exclude = ['organization']
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Person Information', {
            'fields': ['organization', 'name_first', 'name_last', 'title']
        }),
    ]
    inlines = [
        AddressAdminInline,
        EmailAdminInline,
        PhoneAdminInline,
        WebsiteAdminInline,
        ProfileAdminInline,
    ]
    list_display = ('name_first', 'name_last', 'organization')
    list_display_links = ('name_first', 'name_last')
    list_filter = ['organization']
    search_fields = ['organization', 'name_first', 'name_last']

admin.site.register(Person, PersonAdmin)
