# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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
import datetime
import json
import time

import django.views
from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from openstack_dashboard.dashboards.sks.instance import views as instance_views
from openstack_dashboard.dashboards.sks.nova_log_client import nova_log_api


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


class LineChartView(instance_views.IndexView):
    template_name = 'sks/realtime/line_chart.html'
    page_title = _("Instances Overview")

    def get_context_data(self, **kwargs):
        context = {'cinder_meters': [], 'ipmi_meters': [], 'neutron_meters': []}
        context = super(LineChartView, self).get_context_data(**kwargs)

        return context


class InputError(Exception):
    pass


class SamplesView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        period = request.GET.get('period', None)
        date_to_input = request.GET.get('date_to', None)
        date_to = get_date_from_input(date_to_input)
        if date_to is None:
            return HttpResponse("invalid date to input!",
                                status=404)
        log_type = request.GET.get('log_type', None);
        if log_type not in ('info', 'debug', 'error', 'warning', 'other', 'all'):
            return HttpResponse("invalid log type!",
                                status=404)
        if not period.isdigit():
            return HttpResponse("invalid period!",
                                status=404)
        log_count_per_date_list = nova_log_api.get_nova_logs_count_with_period(
            "http://192.168.122.10:9090/nova_log/count_log_with_period/", log_type,
            date_to, period);
        if log_count_per_date_list != 'Error':
            data = []
            for index in log_count_per_date_list:
                for key, value in index.iteritems():
                    data.append({'y': value, 'x': key})
            # series , data_setting = nova_log_api.get_nova_logs_count_by_day()
            series = [{'name': log_type, 'data': data}]
        else:
             return HttpResponse(("Connection Error"), status=404)
        # series = [{'name': log_type, 'data': [{'y': 266376.1843971631, 'x': u'2016-08-27T02:18:30'},
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
        time.sleep(0.5);
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')
