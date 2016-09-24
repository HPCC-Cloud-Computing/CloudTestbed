from horizon.utils import filters as filters_horizon
from django.utils.translation import ugettext_lazy as _
from horizon import tables


class ContainerDockerTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Container Id')
    image = tables.Column('image', verbose_name='Image')
    command = tables.Column('command', verbose_name='Command')
    created = tables.Column('created', verbose_name='Created',
                            filters=(filters_horizon.parse_isotime,filters_horizon.timesince_sortable),)
    state = tables.Column('state', verbose_name='State')
    name = tables.Column('name', verbose_name='Name')

    class Meta(object):
        name = "container_docker"
        verbose_name = _("Container Docker")

