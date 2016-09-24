import time

from django.utils.translation import ugettext_lazy as _
from docker import Client

from horizon import tabs
from openstack_dashboard import api
from openstack_dashboard.dashboards.custom_horizon.linechart_docker import tables as tbl_docker


class Images:
    def __init__(self, imageId, size, repo, tag, created):
        self.id = imageId
        self.size = size
        self.created = created
        self.repo = repo
        self.tag = tag


class Container:
    def __init__(self, containerId, image, command, created, status, name):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.status = status
        self.name = name


class ImageDockerTab(tabs.TableTab):
    name = _("Image Docker")
    slug = "image_docker"
    table_classes = (tbl_docker.ImageDockerTable,)
    template_name = ("horizon/common/_detail_table.html")
    # template_name = "images/images_docker/detail_image.html"
    preload = False

    def get_image_docker_data(self):
        cli = Client(base_url='unix://var/run/docker.sock')
        images = []
        for image in cli.images():
            repo = image['RepoTags']
            repoTags = repo[0]
            create = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(image['Created']))
            repo = repoTags.split(':')[0]
            tag = repoTags.split(':')[1]
            img = Images(image['Id'], image['Size'], repo, tag, create)
            images.append(img)
        return images


class ContainerDockerTab(tabs.TableTab):
    name = _("Container Docker")
    slug = "container_docker"
    table_classes = (tbl_docker.ContainerDockerTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_container_docker_data(self):
        cli = Client(base_url='unix://var/run/docker.sock')
        containers = []
        for ct in cli.containers(all=True):
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            containers.append(Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['Status'], ct['Names'][0][1:]))
        return containers

    # def get_container_docker_data(self):
    #     marker = self.request.GET.get(
    #         tbl_docker.ContainerDockerTable._meta.pagination_param, None)
    #     search_opts = self.get_filters()
    #     filters = {}
    #     if (search_opts.get('name') != None):
    #         filters['name'] = search_opts.get('name')
    #     elif (search_opts.get('id') != None):
    #         filters['id'] = search_opts.get('id')
    #
    #     cli = Client(base_url='unix://var/run/docker.sock')
    #     containers = []
    #     for ct in cli.containers(all=True, filters=filters):
    #         created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
    #         containers.append(
    #             Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], ct['Names'][0][1:]))
    #     return containers
    #
    # def get_filters(self):
    #     # filter_action = self.table._meta._filter_action
    #     # if filter_action:
    #     #     filter_field = self.table.get_filter_field()
    #     #     if filter_action.is_api_filter(filter_field):
    #     #         filter_string = self.table.get_filter_string()
    #     #         if filter_field and filter_string:
    #     #             filters[filter_field] = filter_string
    #     return {'name':'de'}


class ImageDockerTabs(tabs.TabGroup):
    slug = "docker_tabs"
    tabs = (ContainerDockerTab, ImageDockerTab,)
    sticky = True
