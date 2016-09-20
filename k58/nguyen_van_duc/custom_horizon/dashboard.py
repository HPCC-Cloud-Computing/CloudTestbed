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


class Group2(horizon.PanelGroup):
    slug = "group1"
    name = _("Group1")
    panels = ('images_OPS',)


class Group1(horizon.PanelGroup):
    slug = "docker"
    name = _("Docker")
    panels = ('container', 'linechart_docker')


class Custom_Horizon(horizon.Dashboard):
    name = _("Custom_Horizon")
    slug = "custom_horizon"
    panels = (Group1, Group2,)  # Add your panels here.
    default_panel = 'container'  # Specify the slug of the dashboard's default panel.


horizon.register(Custom_Horizon)
