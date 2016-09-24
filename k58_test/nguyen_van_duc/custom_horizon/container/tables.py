from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from docker import Client
from horizon.utils import filters as filters_horizon

from horizon import tables
from collections import defaultdict


class ContainerBasicFilter(tables.FilterAction):
    name = "container_filter"


class ContainerChoiceFilter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Container Name ="), True),
                      ('id', _("Id ="), True),)
    # Tham so True moi gui duoc du lieu sang view


class ContainerFixedFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, value, icon):
            return dict(text=text, value=value, icon=icon)

        buttons = [make_dict(_('Exited'), 'exited', 'fa-stop')]
        buttons.append(make_dict(_('Running'), 'running', 'fa-play'))
        buttons.append(make_dict(_('Created'), 'created', 'fa-check-square'))
        return buttons

    def categorize(self, table, containers):

        tenants = defaultdict(list)
        for container in containers:
            # categories = get_container_categories(container)
            # print categories
            # for category in categories:
            # tenants[category].append(container)
            state = get_container_categories(container)
            tenants[state].append(container)
        return tenants


def get_container_categories(container):
    categories = ''
    if (container.state == 'running'):
        categories = 'running'
    elif(container.state == 'exited'):
        categories = 'exited'
    elif(container.state == 'created'):
        categories = 'created'
    return categories


class UpdateRow(tables.Row):
    ajax = True

    def load_cells(self, container=None):
        super(UpdateRow, self).load_cells(container)
        # Tag the row with the image category for client-side filtering.
        container = self.datum
        category = get_container_categories(container)
        self.classes.append('category-' + category)


class CreateContainer(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Container")
    url = "horizon:custom_horizon:container:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("image", "add_image"),)


class DeleteContainerAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Image",
            u"Delete Images",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Image",
            u"Deleted Images",
            count
        )

    def delete(self, request, obj_id):
        cli = Client(base_url='unix://var/run/docker.sock')

        for container in cli.containers(all=True):
            if (container['Id'][:12] == obj_id):
                cli.remove_container(image=container['Names'][0][1:])
                break;


class ContainerDockerTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Container Id')
    image = tables.Column('image', verbose_name='Image')
    command = tables.Column('command', verbose_name='Command')
    created = tables.Column('created', verbose_name='Created',
                            filters=(filters_horizon.parse_isotime,filters_horizon.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    state = tables.Column('state', verbose_name='State')
    name = tables.Column('name', verbose_name='Name')

    class Meta(object):
        row_class = UpdateRow
        name = "container"
        verbose_name = _("Container")
        table_actions = (ContainerFixedFilter, CreateContainer,)
        multi_select = True