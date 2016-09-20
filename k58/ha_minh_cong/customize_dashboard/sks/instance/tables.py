import logging

from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponse  # noqa
from django import shortcuts
from django import template
from django.template.defaultfilters import title  # noqa
from django.utils.http import urlencode
from django.utils.translation import npgettext_lazy
from django.utils.translation import pgettext_lazy
from django.utils.translation import string_concat  # noqa
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
import six

from horizon import conf
from horizon import exceptions
from horizon import messages
from horizon import tables
from horizon.templatetags import sizeformat
from horizon.utils import filters

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.access_and_security.floating_ips \
    import workflows
from openstack_dashboard.dashboards.project.instances import tabs
from openstack_dashboard.dashboards.project.instances.workflows \
    import resize_instance
from openstack_dashboard.dashboards.project.instances.workflows \
    import update_instance
from openstack_dashboard import policy



LOG = logging.getLogger(__name__)

class StartInstance(policy.PolicyTargetMixin, tables.BatchAction):
    name = "start"
    classes = ('btn-confirm',)
    policy_rules = (("compute", "compute:start"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Start Instance",
            u"Start Instances",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Started Instance",
            u"Started Instances",
            count
        )

    def allowed(self, request, instance):
        return ((instance is None) or
                (instance.status in ("SHUTDOWN", "SHUTOFF", "CRASHED")))

    def action(self, request, obj_id):
        api.nova.server_start(request, obj_id)


POWER_STATES = {
    0: "NO STATE",
    1: "RUNNING",
    2: "BLOCKED",
    3: "PAUSED",
    4: "SHUTDOWN",
    5: "SHUTOFF",
    6: "CRASHED",
    7: "SUSPENDED",
    8: "FAILED",
    9: "BUILDING",
}
def get_power_state(instance):
    return POWER_STATES.get(getattr(instance, "OS-EXT-STS:power_state", 0), '')

def is_deleting(instance):
    task_state = getattr(instance, "OS-EXT-STS:task_state", None)
    if not task_state:
        return False
    return task_state.lower() == "deleting"

class StopInstance(policy.PolicyTargetMixin, tables.BatchAction):
    name = "stop"
    classes = ('btn-danger',)
    policy_rules = (("compute", "compute:stop"),)
    help_text = _("The instance(s) will be shut off.")

    @staticmethod
    def action_present(count):
        return npgettext_lazy(
            "Action to perform (the instance is currently running)",
            u"Shut Off Instance",
            u"Shut Off Instances",
            count
        )

    @staticmethod
    def action_past(count):
        return npgettext_lazy(
            "Past action (the instance is currently already Shut Off)",
            u"Shut Off Instance",
            u"Shut Off Instances",
            count
        )

    def allowed(self, request, instance):
        return ((instance is None)
                or ((get_power_state(instance) in ("RUNNING", "SUSPENDED"))
                    and not is_deleting(instance)))

    def action(self, request, obj_id):
        api.nova.server_stop(request, obj_id)


class LockInstance(policy.PolicyTargetMixin, tables.BatchAction):
    name = "lock"
    policy_rules = (("compute", "compute_extension:admin_actions:lock"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Lock Instance",
            u"Lock Instances",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Locked Instance",
            u"Locked Instances",
            count
        )

    # TODO(akrivoka): When the lock status is added to nova, revisit this
    # to only allow unlocked instances to be locked
    def allowed(self, request, instance):
        if not api.nova.extension_supported('AdminActions', request):
            return False
        return True

    def action(self, request, obj_id):
        api.nova.server_lock(request, obj_id)
class CreateInstance(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Instance")
    url = "horizon:sks:network:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("network", "create_network"),)

class InstanceFilter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Instance Name ="), True),
                      ('status', _("Status ="), True),
                      ('image', _("Image ID ="), True),
                      ('flavor', _("Flavor ID ="), True))
def get_instance_name(instance):
    instance_name = getattr(instance, 'name', )
    if instance_name == '':
        return '(isn\'t have name)' or instance.id
    return instance_name or instance.id

def get_ip_list(instance):
    template_name = 'sks/instance/_instance_ips.html'
    ip_groups = {}

    for ip_group, addresses in six.iteritems(instance.addresses):
        ip_groups[ip_group] = {}
        ip_groups[ip_group]["floating"] = []
        ip_groups[ip_group]["non_floating"] = []

        for address in addresses:
            if ('OS-EXT-IPS:type' in address and
                        address['OS-EXT-IPS:type'] == "floating"):
                ip_groups[ip_group]["floating"].append(address)
            else:
                ip_groups[ip_group]["non_floating"].append(address)

    context = {
        "ip_groups": ip_groups,
    }
    return template.loader.render_to_string(template_name, context)


def get_flavor(instance):
    if hasattr(instance, "full_flavor"):
        template_name = 'sks/instance/_instance_flavor.html'
        size_ram = sizeformat.mb_float_format(instance.full_flavor.ram)
        if instance.full_flavor.disk > 0:
            size_disk = sizeformat.diskgbformat(instance.full_flavor.disk)
        else:
            size_disk = _("%s GB") % "0"
        context = {
            "name": instance.full_flavor.name,
            "id": instance.id,
            "size_disk": size_disk,
            "size_ram": size_ram,
            "vcpus": instance.full_flavor.vcpus,
            "flavor_id": instance.full_flavor.id
        }
        return template.loader.render_to_string(template_name, context)
    return _("Not available")


class InstanceTable(tables.DataTable):
    name = tables.Column(get_instance_name,
                         verbose_name="Name",
                         link="horizon:project:instances:detail")
    image = tables.Column('image_name',verbose_name="Image Name")
    flavor = tables.Column(get_flavor,verbose_name="Flavor")
    ip = tables.Column(get_ip_list,verbose_name="IP Address")
    status = tables.Column('status', verbose_name="Status")
    created = tables.Column("created",
                            verbose_name=_("Time since created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    class Meta(object):
        name = "instances"
        verbose_name = _("Instances")
        #status_columns = ["status"]\
        table_actions = (InstanceFilter,CreateInstance,)
        row_actions = (StartInstance,  LockInstance, StopInstance)
