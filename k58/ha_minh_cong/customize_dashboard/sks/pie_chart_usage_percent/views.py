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


class PieChartProjectUsagePercentView(tables.DataTableView):
    table_class = network_table.NetworkTable
    page_title = _("Project Usage Percent In Pie Chart ")
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
        context = super(PieChartProjectUsagePercentView, self).get_context_data(**kwargs)
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

