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
from horizon import tables
import requests
from django.http import HttpResponse
import json
from openstack_dashboard.dashboards.BASIC.container import tables as project_tables

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'mydashboard/mypanel/index.html'
    table_class = project_tables.ContainerTable

    def get_context_data(self, **kwargs):
        context = super(IndexView,self).get_context_data(**kwargs)
        containers = requestCadvisor()
        container_id = containers.keys()
        container_name = []
        for container in container_id:
            container_name.append(containers[container]['aliases'][0])
        context['container_name'] = container_name
        return context


def requestCadvisor():
    data = requests.get('http://localhost:8080/api/v1.3/docker/')
    containers = data.json()
    return containers

def handleRequest(request):
    containers = requestCadvisor()
    containers_id = containers.keys()
    series = []
    for container in containers_id:
        if (containers[container]['aliases'][0] == request.GET['container_options']):
            series_container ={}
            series_container['name'] = containers[container]['aliases'][0] + ' : ' + request.GET['resource_options']
            stats = containers[container]['stats']
            resource_option = request.GET['resource_options']
            data_resource = []
            if resource_option == 'cpu':
                for stat in stats:
                    data_content = {}
                    data_content['y'] = stat['cpu']['usage']['total']
                    data_content['x'] = stat['timestamp'][:19]
                    data_resource.append(data_content)
            elif resource_option == 'memory':
                for stat in stats:
                    data_content = {}
                    data_content['y'] = stat['memory']['usage']
                    data_content['x'] = stat['timestamp'][:19]
                    data_resource.append(data_content)
            series_container['data'] = data_resource
            series.append(series_container)
    series_json = {
        'series': series,
        'settings': {}
    }
    return HttpResponse(json.dumps(series_json), content_type='application/json')

