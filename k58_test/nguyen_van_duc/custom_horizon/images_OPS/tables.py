
from collections import defaultdict

from django.conf import settings
from django.template import defaultfilters as filters
from django.utils.translation import pgettext_lazy, ungettext_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils.memoized import memoized

from openstack_dashboard import api

def get_format(image):
    format = getattr(image, "disk_format", "")
    # The "container_format" attribute can actually be set to None,
    # which will raise an error if you call upper() on it.
    if not format:
        return format
    # if format != "qcow2":
    #     return
    if format == "raw":
        if getattr(image, "container_format") == 'docker':
            return pgettext_lazy("Image format for display in table",
                                 u"Docker")
        # Most image formats are untranslated acronyms, but raw is a word
        # and should be translated
        return pgettext_lazy("Image format for display in table", u"Raw")
    return format.upper()



class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class OwnerFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, tenant, icon):
            return dict(text=text, value=tenant, icon=icon)

        buttons = [make_dict(_('Project'), 'project', 'fa-home')]
        buttons.append(make_dict(_('ISO'), 'disk_format',
                                 'fa-share-square-o'))
        buttons.append(make_dict(_('Public'), 'public', 'fa-group'))
        return buttons

    def categorize(self, table, images):
        user_tenant_id = table.request.user.tenant_id
        tenants = defaultdict(list)
        for im in images:
            categories = get_image_categories(im, user_tenant_id)
            print categories
            for category in categories:
                tenants[category].append(im)
        return tenants


def get_image_categories(im, user_tenant_id):
    categories = []
    if api.glance.is_image_public(im):
        categories.append('public')
    if im.owner == user_tenant_id:
        categories.append('project')
    if im.disk_format == 'iso':
        categories.append('disk_format')
    # elif im.owner in filter_tenant_ids():
    #     categories.append(im.owner)
    # elif not api.glance.is_image_public(im):
    #     categories.append('shared')

    # if api.glance.is_image_public(im):
    #     categories.append('public')
    # else:
    #     categories.append('project')
    # return categories
    # if im.status == 'active':
    #     categories.append('public')
    # else:
    #     categories.append('project')
    return categories




class CreateImage(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Image")
    url = "horizon:project:images:images:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("image", "add_image"),)



class DeleteImage(tables.DeleteAction):
    # NOTE: The bp/add-batchactions-help-text
    # will add appropriate help text to some batch/delete actions.
    help_text = _("Deleted images are not recoverable.")

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

    policy_rules = (("image", "delete_image"),)

    def allowed(self, request, image=None):
        # Protected images can not be deleted.
        if image and image.protected:
            return False
        if image:
            return image.owner == request.user.tenant_id
        # Return True to allow table-level bulk delete action to appear.
        return True

    def delete(self, request, obj_id):
        api.glance.image_delete(request, obj_id)
        print 'test'


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.glance.image_get(request, image_id)
        return image

    def load_cells(self, image=None):
        super(UpdateRow, self).load_cells(image)
        # Tag the row with the image category for client-side filtering.
        image = self.datum
        my_tenant_id = self.table.request.user.tenant_id
        image_categories = get_image_categories(image, my_tenant_id)
        for category in image_categories:
            self.classes.append('category-' + category)


class ImagesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    status = tables.Column("status", verbose_name=_("Status"))
    public = tables.Column("is_public",
                           verbose_name=_("Public"),
                           empty_value=False,
                           filters=(filters.yesno, filters.capfirst, filters.upper))
    protected = tables.Column("protected",
                              verbose_name=_("Protected"),
                              empty_value=False,
                              filters=(filters.yesno, filters.capfirst))
    disk_format = tables.Column(get_format, verbose_name=_("Disk_Format"))
    size = tables.Column("size",
                         filters=(filters.filesizeformat,),
                         attrs=({"data-type": "size"}),
                         verbose_name=_("Size"))

    class Meta(object):
        row_class = UpdateRow
        name = "images"
        verbose_name = _("Images")
        # status_columns = ["status"]
        # launch_actions = ()
        # row_actions = launch_actions
        table_actions = (CreateImage, OwnerFilter,)
        # table_actions = (CreateImage, MyFilterAction,)
        row_actions = (DeleteImage,)

