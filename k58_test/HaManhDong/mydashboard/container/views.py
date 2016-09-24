
import time

from horizon import tables
from docker import Client
from django.http import HttpResponse
import json
import requests

from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.mydashboard.container import tables as tbl_container

class Container:
    def __init__(self, containerId, image, command, created, state, name):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.state = state
        self.name = name


class IndexView(tables.DataTableView):
    # # A very simple class-based view...
    # template_name = 'mydashboard/container/index.html'
    #
    # def get_data(self):
    #     # Add data to the context here...
    #     dataContainer = []
    #     cli = Client(base_url='unix://var/run/docker.sock')
    #
    #     return dataContainer

    template_name = 'mydashboard/container/index.html'
    table_class = tbl_container.ContainerDockerTable
    # page_title = _("Container")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        m = []
        url = 'http://localhost:8080/api/v1.2/docker'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        dict = r.json()
        keys = dict.keys()
        for key in keys:
            m.append(dict[key]['aliases'][0])
        context['meters'] = m
        return context

    def get_data(self):
        # Add data to the context here...
        cli = Client(base_url='unix://var/run/docker.sock')
        containers = []

        url = 'http://localhost:8080/api/v1.2/docker'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        dict = r.json()
        print "dict: "
        key = dict.keys()
        print dict[key[0]]['aliases'][0]
        # print dict['/docker/c8ad15874022a649545c976a8e09ec7d58b3b7f1389f2303d8669e837e9c8916']['stats']
        # print dict[1]

        for ct in cli.containers(all=True):
            # convert data
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            name = ct['Names'][0][1:]

            containers.append(
                Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name))

        return containers

def convert(id_container):
    url = 'http://localhost:8080/api/v1.2/docker'
    headers = {'content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    dict = r.json()
    key = dict.keys()
    # id_container = key[0]

    dict_info = {'/docker/83295baf0211267805476d142a4537140d6950310632bf6270db43d4ec07ac6a': 'demo1',
                 '/docker/83dd3fce3af7995366bb84b77f18e858b6cf50c651b20a567eaaf82898c9da17': 'demo2',
                 '/docker/dbe6770e3e6cbe1f5fb9c0382f541648f00b29fd6862ba2e0ed2647a784d480e': 'demo3',
                 '/docker/2aea42da8ffb6f6c4328858ab7f8c44654e14c63cc069d7aa20dac9da38fd36b': 'cadvisor1'}
    data_xy = []
    data_y = []

    cli = Client(base_url='unix://var/run/docker.sock')

    i = 0
    for stats in dict[id_container]['stats']:
        data_x = stats['timestamp'][:19]
        yyy = stats['cpu']['usage']['total']
        yyUsage = stats['cpu']['usage']['user']
        if(isinstance(yyUsage,int)):
            print int
        do = yyUsage / yyy
        do = do * 1000000
        print "do:"
        print do
        data_xy.append({'y': stats['cpu']['usage']['per_cpu_usage'][0], 'x': data_x})
        # data_xy.append({'y': data_y[i], 'x': data_x})
        i = i + 1

    return data_xy

def get_data(request):
    if request.method == 'GET':
        meter = request.GET['test2']
        print "meter: "
        print meter

        url = 'http://localhost:8080/api/v1.2/docker'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        dict = r.json()
        keys = dict.keys()
        for key in keys:
            if(dict[key]['aliases'][0] == meter):
                data_xy = convert(key)
                series = [
                    {'meter': u'disk.write.requests',
                     'data': data_xy,
                     'name': u'cadvisor1', 'unit': u'request'},
                ]
                data_setting = {}
                linechart = {'series': series, 'settings': data_setting}
                return HttpResponse(json.dumps(linechart), content_type='application/json')

        data_xy = convert(keys[0])
        series = [
            {'meter': u'disk.write.requests',
             'data': data_xy,
             'name': u'cadvisor1', 'unit': u'request'},
        ]
        data_setting = {}
        linechart = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(linechart), content_type='application/json')