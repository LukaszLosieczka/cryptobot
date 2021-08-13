from resources.models import Organization
from resources.models import Address
from resources.models import Email
from resources.models import Phone
from resources.models import Website
from resources.models import Profile
from django.contrib import admin


class AddressAdminInline(admin.StackedInline):
    model = Address
    exclude = ['person']
    extra = 0


class EmailAdminInline(admin.StackedInline):
    model = Email
    exclude = ['person']
    extra = 0


class PhoneAdminInline(admin.StackedInline):
    model = Phone
    exclude = ['person']
    extra = 0


class WebsiteAdminInline(admin.StackedInline):
    model = Website
    exclude = ['person']
    extra = 0


class ProfileAdminInline(admin.StackedInline):
    model = Profile
    exclude = ['person']
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Organization', {
            'fields': ['name', 'description', 'parent']
        }),
    ]
    inlines = [
        AddressAdminInline,
        EmailAdminInline,
        PhoneAdminInline,
        WebsiteAdminInline,
        ProfileAdminInline,
    ]
    list_display = ('name', 'parent')
    list_display_links = ('name',)
    list_filter = ['parent']
    search_fields = ['name']

admin.site.register(Organization, OrganizationAdmin)
