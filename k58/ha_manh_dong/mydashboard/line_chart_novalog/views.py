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

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from horizon import exceptions
from horizon import tables
import json

from openstack_dashboard.dashboards.mydashboard.line_chart_novalog import tables as log_nova_api_tables

class Log:
	def __init__(self, log_id, time, pid, level):
		self.id = log_id
		self.time = time
		self.pid = pid
		self.level = level

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = log_nova_api_tables.LogNovaTable
    template_name = 'mydashboard/line_chart_novalog/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['meters'] = ["INFO","WARNING","ERROR","All"]
        return context

    def get_data(self):
        # obj = '[{"id": 1, "time": "2015-11-14 00:23:46.664", "pid": 4180, "level": "INFO"}, {"id": 2, "time": "2015-11-14 00:23:46.889", "pid": 4191, "level": "ERROR"}, {"id": 3, "time": "2015-11-14 00:23:47.264", "pid": 4200, "level": "INFO"}, {"id": 4, "time": "2015-11-14 00:23:48.664", "pid": 4180, "level": "WARNING"}, {"id": 5, "time": "2015-11-14 00:23:48.964", "pid": 4191, "level": "INFO"}]'
        # logs = json.loads(obj)
        # context = []
        # for log in logs:
        #     context.append(Log(log['id'], log['time'], log['pid'], log['level']))

        dataLog = readFile('/home/ha/Desktop/log.txt')
        logs =  dataLog[3]

        print (logs)
        return logs
# 2016-09-08 12:22:19.337 3845 WARNING nova.wsgi [-] Stopping WSGI server.
def readFile(fileName):

    obj = []
    id = 0
    dataInfo = []
    numInfo = 0
    dataError = []
    numError = 0
    dataWarning = []
    numWaring = 0
    with open(fileName) as fp:
        for line in fp:
            temp = line.split(' ')
            hour = temp[1].split('.')[0]
            id += 1
            log = Log(id,temp[0]+" "+temp[1],temp[2],temp[3])
            obj.append(log)
            if (temp[3] == 'INFO'):
                numInfo += 1
                dataInfo.append({"y": numInfo, "x": temp[0] + "T" + hour})
            elif(temp[3] == 'ERROR'):
                numError += 1
                dataError.append({"y": numError, "x": temp[0]+"T"+hour})
            else:
                numWaring += 1
                dataWarning.append({"y": numWaring, "x": temp[0]+"T"+hour})
    return (dataInfo,dataWarning,dataError,obj)

def data(request):
    # print request.GET['test']
    meter = request.GET['test']
    dataLog = readFile('/home/ha/Desktop/log.txt')
    print request.GET['date_from']

    ret = getStatus(meter,dataLog)

    # ret = {
    # "series": [
    #   {
    #     "name": "INFO",
    #     "data": [
    #       {"y": 5, "x": "2015-11-14T11:22:25"},
    #       {"y": 10, "x": "2015-11-14T11:22:35"},
    #       {"y": 0, "x": "2015-11-14T11:22:45"},
    #       {"y": 0, "x": "2015-11-14T11:22:55"},
    #       {"y": 15, "x": "2015-11-14T11:23:00"},
    #       {"y": 4, "x": "2015-11-14T11:23:02"},
    #       {"y": 2, "x": "2015-11-14T11:23:05"},
    #       {"y": 10, "x": "2015-11-14T11:23:10"},
    #       {"y": 3, "x": "2015-11-14T11:23:20"}
    #     ]
    #   }, {
    #     "name": "WARNING",
    #     "data": [
    #         {"y": 10, "x": "2015-11-14T11:22:15"},
    #         {"y": 10, "x": "2015-11-14T11:22:17"},
    #         {"y": 5, "x": "2015-11-14T11:22:30"},
    #         {"y": 7, "x": "2015-11-14T11:22:50"},
    #         {"y": 15, "x": "2015-11-14T11:23:00"},
    #         {"y": 24, "x": "2015-11-14T11:23:05"},
    #         {"y": 12, "x": "2015-11-14T11:23:09"},
    #         {"y": 10, "x": "2015-11-14T11:23:13"},
    #         {"y": 30, "x": "2015-11-14T11:23:20"}
    #     ]
    #   }, {
    #     "name": "ERROR",
    #     "data": [
    #         {"y": 9, "x": "2015-11-14T11:22:25"},
    #         {"y": 15, "x": "2015-11-14T11:22:35"},
    #         {"y": 5, "x": "2015-11-14T11:22:45"},
    #         {"y": 15, "x": "2015-11-14T11:22:55"}
    #     ]
    #   }
    # ],
    # "settings": {}
    # }
    return HttpResponse(json.dumps(ret), content_type='application/json')

def getStatus(meter,dataLog):
    if (meter == "INFO"):
        ret = {
            "series": [
                {
                    "name": "INFO",
                    "data": dataLog[0]
                }
            ],
            "settings": {}
        }
    elif (meter == "ERROR"):
        ret = {
            "series": [
                {
                    "name": "ERROR",
                    "data": dataLog[2]
                }
            ],
            "settings": {}
        }
    elif (meter == "WARNING"):
        ret = {
            "series": [
                {
                    "name": "WARNING",
                    "data": dataLog[1]
                }
            ],
            "settings": {}
        }
    else:
        ret = {
            "series": [
                {
                    "name": "INFO",
                    "data": dataLog[0]
                }, {
                    "name": "WARNING",
                    "data": dataLog[1]
                }, {
                    "name": "ERROR",
                    "data": dataLog[2]
                }
            ],
            "settings": {}
        }
    return ret