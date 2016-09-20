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
import datetime
import json
import time

import django.views
from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from openstack_dashboard.dashboards.chart_dashboard.nova_log_client import nova_log_api
from horizon import views


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'chart_dashboard/line_chart/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


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
        data_setting = {}
        time.sleep(0.5);
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')
