from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard import policy

from openstack_dashboard.dashboards.custom_horizon.images_OPS \
    import tables as images_tables

from docker import Client


class IndexView(tables.DataTableView):
    table_class = images_tables.ImagesTable
    template_name = 'custom_horizon/images_OPS/index.html'
    page_title = _("Images")

    # def has_prev_data(self, table):
    #     return getattr(self, "_prev", False)
    #
    # def has_more_data(self, table):
    #     return getattr(self, "_more", False)

    def get_data(self):
        if not policy.check((("image", "get_images"),), self.request):
            msg = _("Insufficient privilege level to retrieve image list.")
            messages.info(self.request, msg)
            return []
        prev_marker = self.request.GET.get(
            images_tables.ImagesTable._meta.prev_pagination_param, None)

        if prev_marker is not None:
            marker = prev_marker
        else:
            marker = self.request.GET.get(
                images_tables.ImagesTable._meta.pagination_param, None)
        reversed_order = prev_marker is not None
        try:
            images, self._more, self._prev = api.glance.image_list_detailed(
                self.request,
                marker=marker,
                paginate=True,
                sort_dir='asc',
                sort_key='name',
                reversed_order=reversed_order
            )

            print images
        except Exception:
            images = []
            self._prev = self._more = False
            exceptions.handle(self.request, _("Unable to retrieve images."))

        return images
