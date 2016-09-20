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
from openstack_dashboard.dashboards.sks.overview import nova_log_api
import django.views
from django.http import HttpResponse  # noqa
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from horizon import exceptions
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard import usage
from openstack_dashboard.dashboards.sks.instance import views as instance_views
from openstack_dashboard.dashboards.sks.network import tables as network_table
import time


class Fake_data:
    inf = 1
    err = 1
    warn = 1
    debg = 1
    other = 1


class SksOverview(tables.DataTableView):
    table_class = network_table.NetworkTable
    page_title = _("Overview")
    template_name = 'sks/overview/sks_usage.html'

    def get_data(self):
        try:
            networks = api.neutron.network_list_for_tenant(self.request, self.request.user.tenant_id)
        except Exception:
            networks = []
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return networks

    class ChartData:
        def __init__(self, data_name, data_value):
            self.name = data_name
            self.data = data_value

    def get_context_data(self, **kwargs):
        context = super(SksOverview, self).get_context_data(**kwargs)
        start_data = self.get_usage_data()
        temp_cpus = []
        temps_ram = []
        temps_disk = []
        for project in start_data:
            temp_cpus.append("{}={}".format(project.project_name + ":" + str(project.vcpus) + "CPUS", project.vcpus))
            temps_ram.append(
                "{}={}".format(project.project_name + ":" + str(project.memory_mb) + "MB", project.memory_mb))
            temps_disk.append(
                "{}={}".format(project.project_name + ":" + str(project.local_gb) + "GB", project.local_gb))
        hypervisor_stats = api.nova.hypervisor_stats(self.request)
        free_ram = hypervisor_stats.memory_mb - hypervisor_stats.memory_mb_used
        free_cpus = hypervisor_stats.vcpus - hypervisor_stats.vcpus_used
        free_disk = hypervisor_stats.local_gb - hypervisor_stats.local_gb_used
        temps_ram.append("{}={}".format("Free_RAM:" + str(free_ram) + "MB", str(free_ram)))
        temp_cpus.append("{}={}".format("Free_CPUS:" + str(free_cpus) + "CPUS", str(free_cpus)))
        temps_disk.append("{}={}".format("Free_Disk:" + str(free_disk) + "GB", str(free_disk)))
        chart_data = [self.ChartData("CPUS", "|".join(temp_cpus)),
                      self.ChartData("RAM", "|".join(temps_ram)),
                      self.ChartData("DISK", "|".join(temps_disk))]
        context['chart_data'] = chart_data
        return context

    def get_usage_data(self):
        today = timezone.now()
        date_start = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
        date_end = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
        data = api.nova.usage_list(self.request, date_start, date_end)
        # Pre-fill project names
        try:
            projects, has_more = api.keystone.tenant_list(self.request)
        except Exception:
            projects = []
            exceptions.handle(self.request,
                              _('Unable to retrieve project list.'))
        for instance in data:
            project = [t for t in projects if t.id == instance.tenant_id]
            # If we could not get the project name, show the tenant_id with
            # a 'Deleted' identifier instead.
            if project:
                instance.project_name = getattr(project[0], "name", None)
            else:
                deleted = _("Deleted")
                instance.project_name = translation.string_concat(
                    instance.tenant_id, " (", deleted, ")")
        return data


class SksBarChartOverview(SksOverview):
    table_class = network_table.NetworkTable
    page_title = _("Bar Chart Overview")
    template_name = 'sks/overview/sks_usage_bar_chart.html'

    class BarChartData:
        def __init__(self, name, used_data, max_value, tool_tip_free):
            self.name = name
            self.used_data = used_data
            self.tool_tip_free = tool_tip_free
            self.max_value = max_value

    def get_context_data(self, **kwargs):
        context = super(SksOverview, self).get_context_data(**kwargs)
        start_data = self.get_usage_data()
        temp_cpus = []
        temps_ram = []
        temps_disk = []
        for project in start_data:
            temp_cpus.append({"tooltip_used": project.project_name + ":" + str(project.vcpus) + "CPUS",
                              "used_instances": project.vcpus})
            temps_ram.append({"tooltip_used": project.project_name + ":" + str(project.memory_mb) + "MB",
                              "used_instances": project.memory_mb})
            temps_disk.append({"tooltip_used": project.project_name + ":" + str(project.local_gb) + "GB",
                               "used_instances": project.local_gb})

        hypervisor_stats = api.nova.hypervisor_stats(self.request)
        free_ram = hypervisor_stats.memory_mb - hypervisor_stats.memory_mb_used
        free_cpus = hypervisor_stats.vcpus - hypervisor_stats.vcpus_used
        free_disk = hypervisor_stats.local_gb - hypervisor_stats.local_gb_used

        context['chart_data_list'] = [
            self.BarChartData("CPUS", json.dumps(temp_cpus), hypervisor_stats.vcpus,
                              "Free CPU:" + str(free_cpus) + "CPUS"),
            self.BarChartData("RAM", json.dumps(temps_ram), hypervisor_stats.memory_mb,
                              "Free RAM:" + str(free_ram) + "MB"),
            self.BarChartData("DISK", json.dumps(temps_disk), hypervisor_stats.local_gb,
                              "Free Disk:" + str(free_disk) + "GB")
        ]
        return context


class ProjectOverview(usage.UsageView):
    table_class = usage.ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'sks/overview/project_usage.html'

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()

    def get_context_data(self, **kwargs):
        context = tables.DataTableView.get_context_data(self, **kwargs)
        context['table'].kwargs['usage'] = self.usage
        context['form'] = self.usage.form
        context['usage'] = self.usage

        context['charts'] = []

        # (Used key, Max key, Human Readable Name, text to display when
        # describing the quota by default it is 'Used')
        types = [("totalInstancesUsed", "maxTotalInstances", _("Instances")),
                 ("totalCoresUsed", "maxTotalCores", _("VCPUs")),
                 ("totalRAMUsed", "maxTotalRAMSize", _("RAM")),
                 ("totalFloatingIpsUsed", "maxTotalFloatingIps",
                  _("Floating IPs"), _("Allocated")),
                 ("totalSecurityGroupsUsed", "maxSecurityGroups",
                  _("Security Groups"))]
        # Check for volume usage
        if 'totalVolumesUsed' in self.usage.limits and self.usage.limits[
            'totalVolumesUsed'] >= 0:
            types.append(("totalVolumesUsed", "maxTotalVolumes",
                          _("Volumes")))
            types.append(("totalGigabytesUsed", "maxTotalVolumeGigabytes",
                          _("Volume Storage")))
        for t in types:
            if t[0] in self.usage.limits and t[1] in self.usage.limits:
                text = False
                if len(t) > 3:
                    text = t[3]
                context['charts'].append({
                    'name': t[2],
                    'used': self.usage.limits[t[0]],
                    'max': self.usage.limits[t[1]],
                    'free': self.usage.limits[t[1]] - self.usage.limits[t[0]],
                    'text': text
                })

        try:
            context['simple_tenant_usage_enabled'] = \
                api.nova.extension_supported('SimpleTenantUsage', self.request)
        except Exception:
            context['simple_tenant_usage_enabled'] = True
        return context


class LineChartView(instance_views.IndexView):
    template_name = 'sks/overview/line_chart.html'
    page_title = _("Instances Overview")

    def get_context_data(self, **kwargs):
        context = {'cinder_meters': [], 'ipmi_meters': [], 'neutron_meters': []}
        context = super(LineChartView, self).get_context_data(**kwargs)

        return context


class NovaLogAndInstance(instance_views.IndexView):
    template_name = 'sks/overview/nova_log.html'
    page_title = _("Instances and Nova Log Summary")


def get_date_from_input(date_input):
    if date_input is None:
        return None
    elif not date_input:
        return "unspecified"
    else:  # 08/24/2016
        try:
            return datetime.datetime.strptime(date_input, "%m/%d/%Y")
        except ValueError:
            return None


class NovaLogSummary(TemplateView):
    template_name = 'sks/overview/s_log_template.html'

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
        if date_from != "unspecified":
            date_from = datetime.datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0)
        t = datetime.datetime.now()
        check_time = datetime.datetime(t.year, t.month, t.day, 00, 00, 00) + datetime.timedelta(days=1, hours=1)
        if date_to != "unspecified":
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
            print("info:" + str(result.info_number) + " warning:" + str(result.warning_number) + " error:" + str(
                result.error_number) +
                  " debug: " + str(result.debug_number))
            return HttpResponse(json.dumps(respond_obj), status=200, content_type="application/json")
        else:
            return HttpResponse(result, status=404)


# write new api for count log from unspecified to end specified
class NovaLogSummaryLineChart(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        date_from = get_date_from_input(request.GET.get('date_from', None))
        date_to = get_date_from_input(request.GET.get('date_to', None))
        series, data_setting = nova_log_api.get_nova_logs_count_by_day(date_from, date_to)

        # time.sleep(4)
        # series = [{'meter': u'disk.write.requests', 'data': [{'y': 266376.1843971631, 'x': u'2016-08-27T02:18:30'},
        #                                                      {'y': 384770.97222222225, 'x': u'2016-08-28T02:18:30'},
        #                                                      {'y': 504014.0833333333, 'x': u'2016-08-29T02:18:30'},
        #                                                      {'y': 624130.2013888889, 'x': u'2016-08-30T02:18:31'}],
        #            'name': u'admin', 'unit': u'request'}]
        # data_setting = {}
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class SamplesView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        time.sleep(4)
        # series , data_setting = nova_log_api.get_nova_logs_count_by_day()

        series = [{'meter': u'disk.write.requests', 'data': [{'y': 266376.1843971631, 'x': u'2016-08-27T02:18:30'},
                                                             {'y': 384770.97222222225, 'x': u'2016-08-28T02:18:30'},
                                                             {'y': 504014.0833333333, 'x': u'2016-08-29T02:18:30'},
                                                             {'y': 624130.2013888889, 'x': u'2016-08-30T02:18:31'}],
                   'name': u'admin', 'unit': u'request'}]
        data_setting = {}
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')
