
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from horizon import exceptions
from horizon import tables
import json

from openstack_dashboard.dashboards.mydashboard.pie_chart_novalog import tables as log_nova_api_tables

class Log:
    def __init__(self,log_id,time,pid,level):
        self.id = log_id
        self.time = time
        self.pid = pid
        self.level = level

    def getArg(self,str):
        return {
            'id': self.id,
            'time': self.time,
            'pid': self.pid,
            'level': self.level
        }.get(str, "")

# class Log:
# 	def __init__(self, log_id, time, pid, level):
# 		self.id = log_id
# 		self.time = time
# 		self.pid = pid
# 		self.level = level
#
#     def getArg(self,str):
#         return {
#             'id': self.id,
#             'time': self.time,
#             'pid': self.pid,
#             'level': self.level
#         }.get(str, "")

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = log_nova_api_tables.LogNovaTable
    template_name = 'mydashboard/pie_chart_novalog/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        dataLog = readFile('/home/ha/Desktop/log.txt')
        context['datapiechart'] = "INFO="+str(dataLog[0])+"|WARNING="+str(dataLog[1])+"|ERROR="+str(dataLog[2])
        return context

    def get_data(self):
        dataLog = readFile('/home/ha/Desktop/log.txt')
        logs =  dataLog[3]

        string_filter = self.get_filters()
        keys = string_filter.keys()
        if keys:
            key = keys[0]
            print "key: " + key
            print "String filter: " + string_filter[key]
            temp = []
            for log in logs:
                if(isinstance(log.getArg(key),int)):
                    t = str(log.getArg(key))
                    if (string_filter[key] == t):
                        temp.append(log)
                elif (string_filter[key] == log.getArg(key)):
                    temp.append(log)
            return temp

        # print (logs)
        return logs

    def get_filters(self):
        filters = {}
        filter_action = self.table._meta._filter_action
        if filter_action:
            filter_field = self.table.get_filter_field()
            if filter_action.is_api_filter(filter_field):
                filter_string = self.table.get_filter_string()
                if filter_field and filter_string:
                    filters[filter_field] = filter_string

        return filters

# 2016-09-08 12:22:19.337 3845 WARNING nova.wsgi [-] Stopping WSGI server.
def readFile(fileName):

    obj = []
    id = 0
    numInfo = 0
    numError = 0
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
            elif(temp[3] == 'ERROR'):
                numError += 1
            else:
                numWaring += 1
    return (numInfo,numWaring,numError,obj)

def data(request):

    # obj = [{"id": 1, "time": "2015-11-14 00:23:46.664", "pid": 4180, "level": "INFO"}, {"id": 2, "time": "2015-11-14 00:23:46.889", "pid": 4191, "level": "ERROR"}, {"id": 3, "time": "2015-11-14 00:23:47.264", "pid": 4200, "level": "INFO"}, {"id": 4, "time": "2015-11-15 00:23:48.664", "pid": 4180, "level": "WARNING"}, {"id": 5, "time": "2015-11-15 00:23:48.964", "pid": 4191, "level": "INFO"}]

    dataLog = readFile('/home/ha/Desktop/log.txt')

    ret = {
        "series": [
            {
                "name": "INFO",
                "data": dataLog[0]
            }, {
                "name": "WARNING",
                "data":dataLog[1]
            }, {
                "name": "ERROR",
                "data": dataLog[2]
            }
        ],
        "settings": {}
    }
    return HttpResponse(json.dumps(ret), content_type='application/json')
