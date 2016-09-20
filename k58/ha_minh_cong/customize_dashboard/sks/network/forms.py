# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
"""
import logging
import netaddr
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

LOG = logging.getLogger(__name__)

from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard import policy

PROVIDER_TYPES = [('local', _('Local')), ('flat', _('Flat')),
                  ('vlan', _('VLAN')), ('gre', _('GRE')),
                  ('vxlan', _('VXLAN'))]


class CreateNetworkForm(forms.SelfHandlingForm):
    network_name = forms.CharField(max_length=255,
                                   label=_("Network Name"),
                                   required=False)
    admin_state = forms.ChoiceField(choices=[(True, _('UP')),
                                             (False, _('DOWN'))],
                                    label=_("Admin State"),
                                    required=False,
                                    help_text=_("The state to start"
                                                " the network in."))
    network_shared = forms.BooleanField(label=_("Shared"), initial=False,
                                        required=False)
    with_subnet = forms.BooleanField(label=_("Create Subnet"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switchable',
                                         'data-slug': 'with_subnet',
                                         'data-hide-on-checked': 'false'
                                     }),
                                     initial=False,
                                     required=False)
    subnet_name = forms.CharField(max_length=255,
                                  widget=forms.TextInput(attrs={
                                      'class': 'switched',
                                      'data-switch-on': 'with_subnet',
                                      'data-source-manual': _("Subnet Name"),
                                  }),
                                  label=_("Subnet Name"),
                                  required=False)
    cidr = forms.IPField(label=_("Network Address"),
                         required=False,
                         initial="",
                         widget=forms.TextInput(attrs={
                             'class': 'switched',
                             'data-switch-on': 'with_subnet',
                             'data-source-manual': _("Network Address")
                         }),
                         help_text=_("Network address in CIDR format "
                                     "(e.g. 192.168.0.0/24, 2001:DB8::/48)"),
                         version=forms.IPv4 | forms.IPv6,
                         mask=True)
    gateway_ip = forms.IPField(
        label=_("Gateway IP"),
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'with_subnet',
            'data-source-manual': _("Gateway IP")
        }),
        required=False,
        initial="",
        help_text=_("IP address of Gateway (e.g. 192.168.0.254) "
                    "The default value is the first IP of the "
                    "network address "
                    "(e.g. 192.168.0.1 for 192.168.0.0/24, "
                    "2001:DB8::1 for 2001:DB8::/48). "
                    "If you use the default, leave blank. "
                    "If you do not want to use a gateway, "
                    "check 'Disable Gateway' below."),
        version=forms.IPv4 | forms.IPv6,
        mask=False)
    enable_dhcp = forms.BooleanField(label=_("Enable DHCP"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switched',
                                         'data-switch-on': 'with_subnet',
                                         # 'data-with_subnet-True': _('Network Address'),
                                         'data-source-manual': _("Enable DHCP"),
                                     }),
                                     initial=True,
                                     required=False)
    dns_nameservers = forms.CharField(
        widget=forms.widgets.Textarea(attrs={'rows': 4,
                                             'class': 'switched',
                                             'data-switch-on': 'with_subnet',
                                             # 'data-with_subnet-True': _('Network Address'),
                                             'data-source-manual': _("Enable DHCP"),
                                             }),
        label=_("DNS Name Servers"),
        help_text=_("IP address list of DNS name servers for this subnet. "
                    "One entry per line."),
        required=False)

    # network_type = forms.ChoiceField(
    #     label=_("Provider Network Type"),
    #     help_text=_("The physical mechanism by which the virtual "
    #                 "network is implemented."),
    #     widget=forms.Select(attrs={
    #         'class': 'switchable',
    #         'data-slug': 'network_type'
    #     }))

    def __init__(self, request, *args, **kwargs):
        super(CreateNetworkForm, self).__init__(request, *args, **kwargs)
        # self.fields['network_type'].choices = PROVIDER_TYPES
        if not policy.check((("network", "create_network:shared"),), request):
            self.fields['shared'].widget = forms.CheckboxInput(
                attrs={'disabled': True})
            self.fields['shared'].help_text = _(
                'Non admin users are not allowed to set shared option.')

    def _convert_ip_address(self, ip, field_name):
        try:
            return netaddr.IPAddress(ip)
        except (netaddr.AddrFormatError, ValueError):
            msg = (_('%(field_name)s: Invalid IP address (value=%(ip)s)')
                   % {'field_name': field_name, 'ip': ip})
            raise forms.ValidationError(msg)

    def _convert_ip_network(self, network, field_name):
        try:
            return netaddr.IPNetwork(network)
        except (netaddr.AddrFormatError, ValueError):
            msg = (_('%(field_name)s: Invalid IP address (value=%(network)s)')
                   % {'field_name': field_name, 'network': network})
            raise forms.ValidationError(msg)

    def _check_dns_nameservers(self, dns_nameservers):
        for ns in dns_nameservers.split('\n'):
            ns = ns.strip()
            if not ns:
                continue
            self._convert_ip_address(ns, "dns_nameservers")

    def _check_subnet_data(self, cleaned_data, is_create=True):
        cidr = cleaned_data.get('cidr')
        gateway_ip = cleaned_data.get('gateway_ip')
        self._check_dns_nameservers(cleaned_data.get('dns_nameservers'))
        if not cidr:
            msg = _('If you choose create subnet, you must specify network address')
            raise forms.ValidationError(msg)
        if cidr:
            ip_version = 4
            subnet = netaddr.IPNetwork(cidr)
            if subnet.version != ip_version:
                msg = _('Network Address and IP version are inconsistent.')
                raise forms.ValidationError(msg)
            if ip_version == 4 and subnet.prefixlen == 32:
                msg = _("The subnet in the Network Address is "
                        "too small (/%s).") % subnet.prefixlen
                self._errors['cidr'] = self.error_class([msg])
        if gateway_ip:
            if netaddr.IPAddress(gateway_ip).version is not 4:
                msg = _('Gateway IP and IP version are inconsistent.')
                raise forms.ValidationError(msg)

    def clean(self):
        cleaned_data = super(CreateNetworkForm, self).clean()
        with_subnet = cleaned_data.get('with_subnet')
        if not with_subnet:
            return cleaned_data
        self._check_subnet_data(cleaned_data)
        return cleaned_data

    def format_status_message(self, message):
        # name = self.context.get('net_name') or self.context.get('net_id', '')
        return message

    def _create_network(self, request, data):
        try:
            params = {'name': data['network_name'],
                      'admin_state_up': (data['admin_state'] == 'True'),
                      'shared': data['network_shared']}
            network = api.neutron.network_create(request, **params)
            # self.context['net_id'] = network.id
            messages.success(request,
                             _('Network "%s" was successfully created.') %
                             network.name_or_id)

            msg = (_('Network "%s" was successfully created.') %
                   network.name_or_id)
            LOG.debug(msg)
            return network
        except Exception as e:
            msg = (_('Failed to create network "%(network)s": %(reason)s') %
                   {"network": data['network_name'], "reason": e})
            LOG.info(msg)
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)
            return False

    def _setup_subnet_parameters(self, params, data, is_create=True):
        if 'cidr' in data and data['cidr']:
            params['cidr'] = data['cidr']
        params['ip_version'] = 4
        if data['gateway_ip']:
            params['gateway_ip'] = data['gateway_ip']
        params['enable_dhcp'] = data['enable_dhcp']
        if data['dns_nameservers']:
            nameservers = [ns.strip()
                           for ns in data['dns_nameservers'].split('\n')
                           if ns.strip()]
            params['dns_nameservers'] = nameservers

    def _create_subnet(self, request, data, network, no_redirect=False):
        network_id = network.id
        network_name = network.name
        try:
            params = {'network_id': network_id,
                      'name': data['subnet_name']}

            self._setup_subnet_parameters(params, data)

            subnet = api.neutron.subnet_create(request, **params)
            # self.context['subnet_id'] = subnet.id
            msg = _('Subnet "%s" was successfully created.') % data['cidr']
            messages.success(request,
                             _('Subnet "%s" was successfully created.') % data['cidr'])

            LOG.debug(msg)
            return subnet
        except Exception as e:
            msg = _('Failed to create subnet "%(sub)s" for network "%(net)s": '
                    ' %(reason)s')
            if no_redirect:
                redirect = None
            else:
                redirect = self.get_failure_url()
            exceptions.handle(request,
                              msg % {"sub": data['cidr'], "net": network_name,
                                     "reason": e},
                              redirect=redirect)
            return False

    def _delete_network(self, request, network):
        """Delete the created network when subnet creation failed."""
        try:
            api.neutron.network_delete(request, network.id)
            msg = _('Delete the created network "%s" '
                    'due to subnet creation failure.') % network.name
            LOG.debug(msg)
            redirect = self.get_failure_url()
            messages.info(request, msg)
            raise exceptions.Http302(redirect)
        except Exception:
            msg = _('Failed to delete network "%s"') % network.name
            LOG.info(msg)
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)

    def handle(self, request, data):
        network = self._create_network(request, data)
        if not network:
            return False
        # If we do not need to create a subnet, return here.
        if not data['with_subnet']:
            return True
        subnet = self._create_subnet(request, data, network, no_redirect=True)
        if subnet:
            return True
        else:
            self._delete_network(request, network)
            return False

    def get_success_url(self):
        return reverse("horizon:sks:network:index")

    def get_failure_url(self):
        return reverse("horizon:sks:network:index")
