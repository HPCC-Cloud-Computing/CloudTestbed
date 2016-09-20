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

from django.utils.translation import ugettext_lazy as _
from openstack_dashboard import api
import logging
from collections import OrderedDict
from horizon import exceptions
from horizon import tabs
from openstack_dashboard.api import base
from openstack_dashboard.api import cinder
from openstack_dashboard.api import heat
from openstack_dashboard.api import keystone
from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova
from openstack_dashboard.dashboards.sks.network \
    import tables as network_table
from openstack_dashboard.dashboards.sks.test_instance \
    import tables as instance_table

INFO_DETAIL_TEMPLATE_NAME = 'horizon/common/_detail_table.html'


class NetworkTab(tabs.TableTab):
    table_classes = (network_table.NetworkTable,)
    name = network_table.NetworkTable.Meta.verbose_name
    slug = network_table.NetworkTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    def get_networks_data(self):
        self.network_more = False
        try:
            networks = api.neutron.network_list_for_tenant(self.request, self.request.user.tenant_id)
            xx = api.neutron.agent_list(request=self.request)
        except Exception:
            networks = []
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return networks

class InstanceTab(tabs.TableTab):
    table_classes = (instance_table.InstanceTable,)
    name = instance_table.InstanceTable.Meta.verbose_name
    slug = instance_table.InstanceTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME
#    permissions = ('openstack.services.compute',)

    def get_instances_data(self):
        marker = self.request.GET.get(
            instance_table.InstanceTable._meta.pagination_param, None)
        #search_opts = self.get_instance_filters({'marker': marker, 'paginate': True})
        search_opts = {'marker': marker, 'paginate': True}
        # Gather our instances
        try:
            instances, instance_more = api.nova.server_list(
                self.request, search_opts=search_opts)

        except Exception:
            instance_more = False
            instances = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instances.'))

        if instances:
            try:
                api.network.servers_update_addresses(self.request, instances)
            except Exception:
                exceptions.handle(
                    self.request,
                    message=_('Unable to retrieve IP addresses from Neutron.'),
                    ignore=True)

            # Gather our flavors and images and correlate our instances to them
            try:
                flavors = api.nova.flavor_list(self.request)
            except Exception:
                flavors = []
                exceptions.handle(self.request, ignore=True)

            try:
                # TODO(gabriel): Handle pagination.
                images, more, prev = api.glance.image_list_detailed(
                    self.request)
            except Exception:
                images = []
                exceptions.handle(self.request, ignore=True)

            full_flavors = OrderedDict([(str(flavor.id), flavor)
                                        for flavor in flavors])
            image_map = OrderedDict([(str(image.id), image)
                                     for image in images])

            # Loop through instances to get flavor info.
            for instance in instances:
                if hasattr(instance, 'image'):
                    # Instance from image returns dict
                    if isinstance(instance.image, dict):
                        if instance.image.get('id') in image_map:
                            instance.image = image_map[instance.image['id']]

                try:
                    flavor_id = instance.flavor["id"]
                    if flavor_id in full_flavors:
                        instance.full_flavor = full_flavors[flavor_id]
                    else:
                        # If the flavor_id is not in full_flavors list,
                        # get it via nova api.
                        instance.full_flavor = api.nova.flavor_get(
                            self.request, flavor_id)
                except Exception:
                    msg = ('Unable to retrieve flavor "%s" for instance "%s".'
                           % (flavor_id, instance.id))
                    # LOG.info(msg)
        return instances


class NetworkInstanceTabs(tabs.TabGroup):
    slug = "system_info"
    # tabs = (InstanceTab,)
    tabs = (InstanceTab, NetworkTab)
    sticky = True
