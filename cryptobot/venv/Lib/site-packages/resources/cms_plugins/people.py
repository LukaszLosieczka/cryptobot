from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from resources.models import PluginOrganization
from resources.models import Person


class PeoplePlugin(CMSPluginBase):
    model = PluginOrganization
    name = _("People")
    render_template = "resources/cms_plugins/people.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        people = Person.objects.filter(organization__name=instance.organization)
        context.update({
            'instance': instance,
            'people': people,
            'organization': instance.organization,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(PeoplePlugin)
