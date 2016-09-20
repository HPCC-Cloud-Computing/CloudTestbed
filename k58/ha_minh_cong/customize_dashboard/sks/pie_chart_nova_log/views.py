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

from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from openstack_dashboard.dashboards.sks.instance import views as instance_views
from openstack_dashboard.dashboards.sks.nova_log_client import nova_log_api


class Fake_data:
    inf = 1
    err = 1
    warn = 1
    debg = 1
    other = 1


class NovaLogView(instance_views.IndexView):
    template_name = 'sks/pie_chart_nova_log/nova_log.html'
    page_title = _("Instances and Nova Log Summary")


def get_date_from_input(date_input):
    if date_input is None:
        return None
    elif not date_input:
        return "none"
    else:  # 08/24/2016
        try:
            return datetime.datetime.strptime(date_input, "%m/%d/%Y")
        except ValueError:
            return None


class NovaLogSummaryAPI(TemplateView):
    template_name = 'sks/pie_chart_nova_log/s_log_template.html'

    class LogCount:
        def __init__(self, name, count):
            self.name = name
            self.count = count

    def post(self, request):
        date_from_data = request.POST.get("date_from")
        date_to_data = request.POST.get("date_to")
        date_from = get_date_from_input(date_from_data)
        date_to = get_date_from_input(date_to_data)
        if date_from is None or date_to is None:
            return HttpResponse("invalid date from or date to input!",
                                status=404)
        if isinstance(date_from, datetime.date) and isinstance(date_to, datetime.date) and date_from > date_to:
            return HttpResponse("Date from must be smaller than date to!",
                                status=404)
        if date_from != "none":
            date_from = datetime.datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0)
        t = datetime.datetime.now()
        check_time = datetime.datetime(t.year, t.month, t.day, 00, 00, 00) + datetime.timedelta(days=1, hours=1)
        if date_to != "none":
            date_to = datetime.datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
            # if date_to>check_time:
            #     return HttpResponse("invalid date to input!",
            #                     status=404)
        # customize endpoint 192.168.122.10:9090

        result = nova_log_api.get_nova_log_summary("http://192.168.122.10:9090/nova_log/summary", date_from, date_to)
        if isinstance(result, nova_log_api.LogSummary):
            respond_obj = {"log_list": [self.LogCount("Info", result.info_number).__dict__,
                                        self.LogCount("Warning", result.warning_number).__dict__,
                                        self.LogCount("Error", result.error_number).__dict__,
                                        self.LogCount("Debug", result.debug_number).__dict__,
                                        self.LogCount("Other", result.other_number).__dict__
                                        ]}
            Fake_data.debg += 1
            Fake_data.inf += 1
            Fake_data.err += 2
            Fake_data.other += 1
            Fake_data.warn += 2
            respond_obj = {"log_list": [self.LogCount("Info", Fake_data.inf).__dict__,
                                        self.LogCount("Warning", Fake_data.warn).__dict__,
                                        self.LogCount("Error", Fake_data.err).__dict__,
                                        self.LogCount("Debug", Fake_data.debg).__dict__,
                                        self.LogCount("Other", Fake_data.other).__dict__
                                        ]}
            print("info:"+str(result.info_number)+" warning:"+str(result.warning_number)+" error:"+str(result.error_number)+
                  " debug: "+str(result.debug_number))
            return HttpResponse(json.dumps(respond_obj), status=200, content_type="application/json")
        else:
            return HttpResponse(result, status=404)
