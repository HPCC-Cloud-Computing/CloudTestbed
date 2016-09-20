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


class ProjectOverview(usage.UsageView):
    table_class = usage.ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'sks/bar_chart/project_usage.html'

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

