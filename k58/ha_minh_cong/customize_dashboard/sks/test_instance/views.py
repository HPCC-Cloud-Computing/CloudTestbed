# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
from collections import OrderedDict

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.sks.network \
    import tables as network_table
from openstack_dashboard.dashboards.sks.test_instance \
    import tables as instance_table
from openstack_dashboard.dashboards.sks.test_instance.neutron_api import neutron_hsk_api

LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = (instance_table.InstanceTable, network_table.NetworkTable)
    template_name = 'sks/test_instance/index.html'
    # page_title = '{{ network.name | default:network.id }}'
    page_title = "SCX"

    def has_more_data(self, table):
        if (table.name == 'instances'):
            return self.instance_more
        elif (table.name == 'networks'):
            return self.network_more
        return False

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

    # def get_instance_filters(self, filters):
    #     filter_action = self._tables['instances']._meta._filter_action
    #     if filter_action:
    #         filter_field = self._tables['instances'].get_filter_field()
    #         if filter_action.is_api_filter(filter_field):
    #             filter_string = self._tables['instances'].get_filter_string()
    #             if filter_field and filter_string:
    #                 filters[filter_field] = filter_string
    #     return filters

    def get_instances_data(self):
        marker = self.request.GET.get(
            instance_table.InstanceTable._meta.pagination_param, None)
        #search_opts = self.get_instance_filters({'marker': marker, 'paginate': True})
        search_opts = {'marker': marker, 'paginate': True}
        # Gather our instances
        try:
            instances, self.instance_more = api.nova.server_list(
                self.request, search_opts=search_opts)

        except Exception:
            self.instance_more = False
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
                    LOG.info(msg)
        return instances

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["agents"] = neutron_hsk_api.agent_list(request=self.request)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:project:networks:index')
