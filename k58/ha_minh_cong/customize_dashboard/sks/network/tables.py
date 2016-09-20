from django.utils.http import urlencode
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.template import defaultfilters as filters
from horizon.utils.memoized import memoized  # noqa

from horizon import tables
from django import template
from openstack_dashboard import api


class CreateNetwork(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Network")
    url = "horizon:sks:network:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("network", "create_network"),)


class DeleteNetwork(tables.DeleteAction):
    # NOTE: The bp/add-batchactions-help-text
    # will add appropriate help text to some batch/delete actions.
    help_text = _("Deleted images are not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Network",
            u"Delete Networks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Network",
            u"Deleted Network",
            count
        )

    policy_rules = (("network", "delete_network"),)

    def allowed(self, request, network=None):
        if network:
            return network.tenant_id == request.user.tenant_id
        # Return True to allow table-level bulk delete action to appear.
        return True

    def delete(self, request, obj_id):
        api.neutron.network_delete(request, obj_id)


class EditNetwork(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Network")
    url = "horizon:sks:network:edit"
    classes = ("ajax-modal",)
    icon = "pencil"
    #policy_rules = (("network", "modify_network"),)

    def allowed(self, request, network=None):
        if network:
            return network.status in ("active","ACTIVE") and \
                   network.tenant_id == request.user.tenant_id
        # We don't have bulk editing, so if there isn't an image that's
        # authorized, don't allow the action.
        return False


class AddSubnet(tables.LinkAction):
    name = "add_subnet"
    verbose_name = _("Add Subnet")
    url = "horizon:sks:network:add_subnet"
    classes = ("ajax-modal",)
    icon = "pencil"
    #policy_rules = (("network", "modify_network"),)

    def allowed(self, request, network=None):
        if network:
            return network.status in ("active","ACTIVE") and \
                   network.tenant_id == request.user.tenant_id
        # We don't have bulk editing, so if there isn't an image that's
        # authorized, don't allow the action.
        return False

class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, network_id):
        network = api.neutron.network_get(request, network_id)
        return network


class NetworkFilter(tables.FilterAction):
    name = 'network_filter'


def get_network_name(network):
    network_name = getattr(network, 'name', )
    if network_name == '':
        return '(isn\'t have name)' or network.id
    return network_name or network.id


def get_subnets(network):
    subnet_template = 'sks/network/_render_subnet.html'
    context = {'subnets': network.subnets}
    return template.loader.render_to_string(subnet_template, context)


def get_network_type(network):
    return getattr(network, 'provider__network_type')


class NetworkTable(tables.DataTable):
    TYPE_CHOICES = (
        ("flat", pgettext_lazy("Type of an image", u"Flat")),
        ("vlan", pgettext_lazy("Type of an image", u"VLAN")),
        ("vxlan", pgettext_lazy("Type of an image", u"VXLAN")),
        ("gre", pgettext_lazy("Type of an image", u"GRE")),

    )
    name = tables.Column(get_network_name,
                         verbose_name=_("Network Name"),
                         truncate=40,
                         link="horizon:sks:network:detail",
                         )
    # network_type = tables.Column(get_network_type,
    #                              verbose_name=_("Type"),
    #                              display_choices=TYPE_CHOICES)
    subnets = tables.Column(get_subnets,
                            verbose_name=_("Subnets Associate"), )
    share = tables.Column('shared', verbose_name=_("Shared"), empty_value=False,
                          filters=(filters.yesno, filters.capfirst))

    def __init__(self, request, *args, **kwargs):
        # role_admin = False
        # for role in request.user.roles:
        #     if role['name'] == 'admin':
        #         role_admin = True
        #         break
        # if not role_admin:
        #     pass
        #     self._columns['network_type'] = None
        super(NetworkTable, self).__init__(request, *args, **kwargs)



    class Meta(object):
        verbose_name = _("Networks")
        name = "networks"
        table_actions = (NetworkFilter, CreateNetwork, DeleteNetwork,)
        row_actions =  (EditNetwork, DeleteNetwork, AddSubnet,)


