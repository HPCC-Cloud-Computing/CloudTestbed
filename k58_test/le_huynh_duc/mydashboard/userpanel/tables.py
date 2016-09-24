from horizon import tables
from docker import Client
# from openstack_dashboard.dashboards.mydashboard.userpanel.views import IndexView
from django.utils.translation import ungettext_lazy
class FilterImageAction(tables.FilterAction):
    def filter(self, table, imagedocker, filter_string):
        q = filter_string.low()
        return [ image for image in imagedocker
                    if q in image.repoTags.low()
                    ]

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
        cli = Client(base_url='unix://var/run/docker.sock')

        img_re = None
        imgs = cli.images()
        for img in imgs:
            print(img['Id'])
            if img['Id'] == obj_id:
                print('ket qua:',img['Id'])
                img_re = img
                break
        print(img_re)
        cli.remove_image(image=img_re,force=True)


class ImageDocker(tables.DataTable):

    size = tables.Column('size',verbose_name='Size')

    created = tables.Column('created',verbose_name='Created',)

    parentId = tables.Column('parentId',verbose_name='ParentId',)

    imageId = tables.Column('imageId',verbose_name='Id',truncate= 10)

    repoTags = tables.Column('repoTags',verbose_name='RepoTags')

    virtualSize = tables.Column('virtualSize',verbose_name='Virtual Size')

    class Meta(object):
        name = 'imagedocker'
        multi_select = True
        table_actions = (FilterImageAction,DeleteImageAction,)
        row_actions = (DeleteImageAction,)



