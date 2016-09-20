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
from docutils.nodes import table
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized
from openstack_dashboard.dashboards.sks.network import forms as network_forms


from openstack_dashboard import api
from openstack_dashboard.utils import filters

from horizon import views
from horizon import  tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.sks.network import tables as network_table
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions


class IndexView(tables.DataTableView):

    table_class = network_table.NetworkTable
    template_name = 'sks/network/index.html'
    page_title = _("Network")

    def get_data(self):
        # Add data to the context here...
        try:
            networks = api.neutron.network_list_for_tenant(self.request, self.request.user.tenant_id)
        except Exception:
            networks = []
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return networks


class DetailView(views.APIView):
    # A very simple class-based view...
    template_name = 'sks/network/index.html'

    def get_data(self, request, context, *args, **kwargs):
        #print (self.kwargs['subnet_id'])

        # Add data to the context here...
        return context


class CreateView(forms.ModalFormView):
    form_class = network_forms.CreateNetworkForm
    form_id = "create_network_form"
    modal_header = _("Create A Network")
    submit_label = _("Create Network")
    submit_url = reverse_lazy('horizon:sks:network:create')
    template_name = 'sks/network/create.html'
    context_object_name = 'image'
    success_url = reverse_lazy("horizon:sks:network:index")
    page_title = _("Create A Network")

    def get_initial(self):
        initial = {}
        for name in [
            'name',
            'description',
            'image_url',
            'source_type',
            'architecture',
            'disk_format',
            'minimum_disk',
            'minimum_ram'
        ]:
            tmp = self.request.GET.get(name)
            if tmp:
                initial[name] = tmp
        return initial


class EditView(views.APIView):
    # A very simple class-based view...
    template_name = 'sks/network/index.html'

    def get_data(self, request, context, *args, **kwargs):
        #print (self.kwargs['subnet_id'])

        # Add data to the context here...
        return context

class AddSubnetView(views.APIView):
    # A very simple class-based view...
    template_name = 'sks/network/index.html'

    def get_data(self, request, context, *args, **kwargs):
        #print (self.kwargs['subnet_id'])

        # Add data to the context here...
        return context

