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

import horizon


class ChartGroup(horizon.PanelGroup):
    slug = "chart_panel"
    name = _("Chart Group")
    panels = ('overview','bar_chart','bar_chart_usage_percent','pie_chart_usage_percent','pie_chart_nova_log',
              'line_chart_nova_log','line_chart_nova_log_2','line_chart_nova_log_test_lab',
              'realtime')


class TableGroup(horizon.PanelGroup):
    slug = "table_panel"
    name = _("Table Group")
    panels = ('network_instance','test_instance','network', 'instance', 'subnet',)
# # # Specify the slug of the default panel.
# class Mygroup(horizon.PanelGroup):
#     slug = "overview_panel"
#     name = _("Chart Group")
#     panels = ('overview',)


class SKS(horizon.Dashboard):
    name = _("SKS")
    slug = "sks"
    panels = (ChartGroup,TableGroup,)  # Add your panels here.
    default_panel = 'overview'  # Specify the slug of the dashboard's default panel.


horizon.register(SKS)
