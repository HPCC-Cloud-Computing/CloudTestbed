from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from docker import Client
from horizon.utils import filters as filters_horizon

from horizon import tables


class FilterImageAction(tables.FilterAction):
    # def filter(self, table, imagedocker, filter_string):
    #     q = filter_string.low()
    #     return [image for image in imagedocker
    #                 if q in image.repoTags.low()
    #             ]
    name = "myfilter"


class DeleteImageAction(tables.DeleteAction):
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
        print 'test'
        cli = Client(base_url='unix://var/run/docker.sock')

        img_re = None
        imgs = cli.images()
        for img in imgs:
            print(img['Id'])
            if img['Id'] == obj_id:
                print('ket qua:', img['Id'])
                img_re = img
                break
        print(img_re)
        cli.remove_image(image=img_re, force=True)


class ImageDockerTable(tables.DataTable):
    repo = tables.Column('repo', verbose_name='Repository')
    tag = tables.Column('tag', verbose_name='Tag')
    created = tables.Column('created', verbose_name='Created', filters=(filters_horizon.parse_isotime,
                                                                        filters_horizon.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    size = tables.Column('size', filters=(filters.filesizeformat,),
                         attrs=({"data-type": "size"}), verbose_name='Size')

    class Meta(object):
        name = "image_docker"
        verbose_name = _("Image Docker")
        table_actions = (FilterImageAction, DeleteImageAction,)
        row_actions = (DeleteImageAction,)


class ContainerDockerTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Container Id')
    image = tables.Column('image', verbose_name='Image')
    command = tables.Column('command', verbose_name='Command')
    created = tables.Column('created', verbose_name='Created', filters=(filters_horizon.parse_isotime,
                                                                        filters_horizon.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    status = tables.Column('status', verbose_name='Status')
    name = tables.Column('name', verbose_name='Name')

    class Meta(object):
        name = "container_docker"
        verbose_name = _("Container Docker")
        table_actions = (FilterImageAction,)
