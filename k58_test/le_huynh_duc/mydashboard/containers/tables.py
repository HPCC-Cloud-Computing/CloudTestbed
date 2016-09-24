from horizon import tables
from django.utils.translation import ungettext_lazy
from docker import Client

class FilterContainerAction(tables.FilterAction):
    def filter(self, table, containers, filter_string):
        q = filter_string.low()
        return [container for container in containers
                    if q in container.names.low() or q in container.image.low()
                ]
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

        contain_re = None
        containers = cli.containers(all=True)
        for container in containers:
            if container['Id'] == obj_id:
                contain_re = container
                break
        cli.remove_container(container=contain_re,force=True,link=False,v=False)

class CreateContainerAction(tables.LinkAction):
    name = 'create'
    url = 'horizon:mydashboard:containers:create'
    verbose_name = 'Create Container'
    classes = ("ajax-modal",)

class ContainerTable(tables.DataTable):
    status = tables.Column('status',verbose_name='Status')
    created = tables.Column('created',verbose_name='Created')
    image = tables.Column('image',verbose_name='Image',truncate=30)
    imageID = tables.Column('imageID',verbose_name='ImageID',truncate=15)

    state = tables.Column('state',verbose_name='State')
    command = tables.Column('command',verbose_name='Command')
    names= tables.Column('names',verbose_name='Names')
    containerId = tables.Column('containerId',verbose_name='Id',truncate=15)

    class Meta(object):
        name = 'containers'
        multi_select = True
        table_actions = (FilterContainerAction,DeleteContainerAction,CreateContainerAction,)
        row_actions = (DeleteContainerAction,)