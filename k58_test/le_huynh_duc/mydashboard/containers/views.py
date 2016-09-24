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

from horizon import tables
from docker import Client
from openstack_dashboard.dashboards.mydashboard.containers import tables as project_tables
from horizon import forms
from openstack_dashboard.dashboards.mydashboard.containers import forms as project_forms
from django.core.urlresolvers import reverse_lazy

class Container:
    def __init__(self,status,created,image,imageID,state,command,names,containerId):
        self.id = containerId
        self.status = status
        self.created = created
        self.image = image
        self.imageID = imageID
        self.state = state
        self.command = command
        self.names = names
        self.containerId = containerId

class CreateContainer(forms.ModalFormView):
    template_name = "mydashboard/containers/create.html"
    modal_header = "Create Container"
    form_class = project_forms.CreateContainer
    submit_url = "horizon:mydashboard:containers:create"
    success_url = reverse_lazy("horizon:mydashboard:containers:index")
    page_title = "Create Container"

    def dispatch(self, *args, **kwargs):
        return super(CreateContainer, self).dispatch(*args, **kwargs)

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'mydashboard/containers/index.html'
    table_class = project_tables.ContainerTable
    page_title = 'Containers Docker'

    def get_data(self):
        # Add data to the context here...
        contains = []
        cli = Client(base_url='unix://var/run/docker.sock')
        containers = cli.containers(all=True)
        for container in containers:
            contain = Container(container['Status'],container['Created'],container['Image'],
                                container['ImageID'],container['State'],container['Command'],container['Names'],container['Id'])
            # print(contain.id,contain.status,contain.status,contain.names,contain.command,contain.containerId)
            contains.append(contain)

        return contains
