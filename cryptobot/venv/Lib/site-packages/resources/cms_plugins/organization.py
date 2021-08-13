from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from resources.models import PluginOrganization


class OrganizationPlugin(CMSPluginBase):
    model = PluginOrganization
    name = _("Organization")
    render_template = "resources/cms_plugins/organization.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'organization': instance.organization,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(OrganizationPlugin)
