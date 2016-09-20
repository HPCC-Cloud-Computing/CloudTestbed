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

# from horizon import views
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from openstack_dashboard.dashboards.sks.network_instance import tabs as network_instance_tabs
from openstack_dashboard.dashboards.sks.test_instance.neutron_api import neutron_hsk_api


class IndexView(tabs.TabbedTableView):
    tab_group_class = network_instance_tabs.NetworkInstanceTabs
    template_name = 'sks/network_instance/index.html'
    page_title = _("Instance and Network")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        # try:
        #     context["version"] = version.version_info.version_string()
        # except Exception:
        #     exceptions.handle(self.request,
        #                       _('Unable to retrieve version information.'))
        context = super(IndexView, self).get_context_data(**kwargs)
        context["agents"] = neutron_hsk_api.agent_list(request=self.request)
        return context
