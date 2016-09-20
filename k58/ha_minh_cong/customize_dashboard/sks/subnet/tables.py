from django.utils.http import urlencode
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.template import defaultfilters as filters

from horizon import tables


def get_subnet_name(subnet):
    subnet_name = getattr(subnet,'name',)
    if subnet_name == '':
        return '(isn\'t have name)' or subnet.id
    return subnet_name or subnet.id


def get_allocation_pools(subnet):
    ip_pools = getattr(subnet,"allocation_pools",None)
    if ip_pools is not None:
        subnet_pools =''
        for pool in ip_pools:
            subnet_pools+= pool['start']+' - '+pool['end']+';'
        return subnet_pools
    else:
        return None




class SubnetTable(tables.DataTable):
    name = tables.Column(get_subnet_name,
                         verbose_name=_("Subnet Name"),
                         truncate=40,
                         link="horizon:sks:subnet:detail",
                         )
    enable_dhcp = tables.Column('enable_dhcp', verbose_name="Enable DHCP", empty_value=False,
                                filters=(filters.yesno, filters.capfirst))
    network_id = tables.Column('network_id', verbose_name="Network ID", empty_value=False)
    allocation_pools = tables.Column(get_allocation_pools, verbose_name="Allocation pools")
    cidr = tables.Column("cidr", verbose_name="CIDR")
    gateway_ip = tables.Column("gateway_ip", verbose_name="Gateway IP", empty_value='-')


