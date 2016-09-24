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
from __future__ import division
from horizon import views
import datetime
import json
import time
import openstack_dashboard.dashboards.docker.realtime_panel.docker_api as docker_api
import django.views
from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView



def get_date_from_input(date_input):
    if date_input is None:
        return None
    elif not date_input:
        return "none"
    else:  # 08/24/2016
        try:
            return datetime.datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            return None


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'docker/realtime_panel/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class DockerData(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        date_from_data = request.GET.get("date_from")
        date_to_data = request.GET.get("date_to")
        date_from = get_date_from_input(date_from_data)
        date_to = get_date_from_input(date_to_data)
        if date_from is None or date_to is None:
            return HttpResponse("invalid date from or date to input!",
                                status=404)
        if isinstance(date_from, datetime.date) and isinstance(date_to, datetime.date) and \
                (date_from > date_to or date_to > date_from + datetime.timedelta(days=5)):
            date_from = date_to - datetime.timedelta(days=5)
        # log_type = request.GET.get('log_type', None)
        # if log_type not in ('info', 'debug', 'error', 'warning', 'other', 'all'):
        #     return HttpResponse("invalid log type!",
        #                         status=404)
        containers_info = docker_api.get_all_container_data()
        #     "http://192.168.122.10:9090/nova_log/count_log_per_day", log_type,
        #     date_from, date_to);
        # # if log_count_per_date_list != 'Error':
        #     data = []
        #     for index in log_count_per_date_list:
        #         for key, value in index.iteritems():
        #             data.append({'y': value, 'x': key})
        #     # series , data_setting = nova_log_api.get_nova_logs_count_by_day()
        #     series = [{'name': log_type, 'data': data}]
        # else:
        #     return HttpResponse(("Connection Error"), status=404)
        # print (containers_info)
        series = []
        for name, ctn_info in containers_info.iteritems():
            container_index = {"name": ctn_info['aliases'][0]}
            container_index_data = []
            for data_in_timestamp in ctn_info['stats']:
                container_index_data.append(
                    {"x": data_in_timestamp['timestamp'][0:19], 'y': data_in_timestamp['cpu']['usage']["total"]/ ((1.0)*data_in_timestamp['cpu']['usage']["system"])})
            container_index['data'] = container_index_data
            series.append(container_index)
        # series = [{'name': "info", 'data': [{'y': 266376.1843971631, 'x': u'2016-08-27T02:18:30'},
        #                                                      {'y': 384770.97222222225, 'x': u'2016-08-28T02:18:30'},
        #                                                      {'y': 504014.0833333333, 'x': u'2016-08-29T02:18:30'},
        #                                                      {'y': 624130.2013888889, 'x': u'2016-08-30T02:18:31'}],},
        #           {'name': u'demo', 'data': [{'y': 100000.1843971631, 'x': u'2016-08-27T02:18:30'},
        #                                       {'y': 110000.97222222225, 'x': u'2016-08-28T02:18:30'},
        #                                       {'y': 120000.0833333333, 'x': u'2016-08-29T02:18:30'},
        #                                       {'y': 130000.2013888889, 'x': u'2016-08-30T02:18:31'}],}
        #
        #           ]
        data_setting = {}
        # time.sleep(0.5);
        # ret = {'series': series, 'settings': data_setting}
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')
