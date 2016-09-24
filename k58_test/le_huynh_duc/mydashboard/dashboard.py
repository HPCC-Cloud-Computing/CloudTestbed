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

class ContainerGroup(horizon.PanelGroup):
    slug = "containerGroup"
    name = _("Container")
    panels = ('docker',)

class Mygroup(horizon.PanelGroup):
    slug = "mygroup"
    name = _("My Group")
    panels = ('mypanel',)

class Usergroup(horizon.PanelGroup):
    slug = "usergroup"
    name = _("Docker Local")
    panels = ('userpanel','containers')

class Mydashboard(horizon.Dashboard):
    name = _("My Dashboard")
    slug = "mydashboard"
    panels = (Mygroup,Usergroup,ContainerGroup)  # Add your panels here.
    default_panel = 'mypanel'  # Specify the slug of the dashboard's default panel.


horizon.register(Mydashboard)
